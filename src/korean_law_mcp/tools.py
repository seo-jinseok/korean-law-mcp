import logging
import re
from .server import mcp
from .utils import (
    client, 
    search_statute_internal, 
    smart_search_statute_internal, 
    search_integrated_internal,
    get_statute_detail_internal,
    get_precedent_detail_internal,
    get_admin_rule_detail_internal,
    get_prec_const_detail_internal,
    get_autonomous_law_detail_internal,
    get_legal_term_detail_internal,
    get_statutory_interpretation_detail_internal,
    resolve_references,
    _parse_articles
)

logger = logging.getLogger("korean-law-mcp")

@mcp.tool()
def search_korean_law(query: str) -> str:
    """
    Primary interface for searching Korean laws, precedents, and administrative rules.
    It is a "Smart Search" that adapts to the query type.

    Capabilities:
    1. **Specific Article Lookup** (Preferred):
       - Input: "Civil Act Article 103", "민법 제103조", "Criminal Act 250"
       - Behavior: Returns the *exact content* of the article directly. No need for further steps.
       - Note: Supports both Korean ("민법") and major English names ("Civil Act").

    2. **Broad Keyword Search**:
       - Input: "school violence", "학교폭력", "adultery case"
       - Behavior: Returns a summarized list of top results across Statutes, Precedents, and Admin Rules.
       - Output: Includes **Typed IDs** (e.g., `statute:12345`, `prec:67890`) which MUST be used with `read_legal_resource` to get full text.

    Usage Tips:
    - ALWAYS try to be specific if you know the law name and article number.
    - If searching for a case by number, just enter it (e.g., "2010다102991").
    - **NEW:** To find specific articles containing keywords (e.g., "credits" in "Higher Education Act"), first search for the law to get its ID, then use `search_law_articles(law_id, "keywords")`.
    """
    # 0. English to Korean Mapping for major laws
    ENGLISH_LAW_MAPPING = {
        "civil act": "민법",
        "criminal act": "형법",
        "commercial act": "상법",
        "constitution": "대한민국헌법",
        "administrative procedures act": "행정절차법",
        "labor standards act": "근로기준법",
        "school violence": "학교폭력"
    }
    
    lower_query = query.lower()
    for eng, kor in ENGLISH_LAW_MAPPING.items():
        if eng in lower_query:
            query = re.sub(eng, kor, query, flags=re.IGNORECASE)
            logger.info(f"Translated English query to: {query}")
            break

    # 1. Check for specific article pattern (smart search) -> Direct content
    # Patterns: "제10조", "Article 10", or "Law 10" (relaxed)
    if (re.search(r'제\s*\d+조', query) or 
        "Article" in query or 
        re.search(r'(?:\s|^)\d+(?:-\d+)?(?:\s|$)', query)):
        # It's likely a specific article request
        return smart_search_statute_internal(query)
    
    # 2. Otherwise default to integrated search
    return search_integrated_internal(query)

@mcp.tool()
def search_law_articles(law_id: str, keywords: str) -> str:
    """
    Search for specific keywords within the articles of a statute.
    
    Args:
        law_id: The ID of the law (e.g., "statute:12345" or just "12345").
        keywords: Space-separated keywords to search for within article text.
        
    Returns:
        Markdown formatted text containing the articles that match the keywords.
    """
    # Remove prefix if present
    if ":" in law_id:
        law_id = law_id.split(":")[-1]
        
    logger.info(f"Searching articles in law {law_id} for: {keywords}")
    
    data = client.get_law_detail(law_id)
    if '법령' not in data: 
        return "Error: Law not found or invalid ID."
        
    law_info = data['법령']
    law_name = law_info.get('기본정보', {}).get('법령명_한글', 'Unknown')
    parsed_articles = _parse_articles(law_info)
    
    if not parsed_articles: 
        return f"# {law_name}\n\n(No articles found to search)"
    
    matches = []
    keywords_list = keywords.split()
    
    for art in parsed_articles:
        # Check if all keywords are in the article text
        # Simple case-insensitive match
        text_to_search = art['full_text']
        if all(k in text_to_search for k in keywords_list):
            matches.append(art)
            
    if not matches:
        return f"# {law_name}\n\nNo articles found matching keywords: '{keywords}'"
        
    output = [f"# {law_name} - Search Results for '{keywords}'", ""]
    output.append(f"Found {len(matches)} matching articles.\n")
    
    for art in matches:
        output.append(f"## 제{art['no']}조 {art['title'] if art['title'] else ''}")
        output.append(art['full_text'])
        output.append("")
        
    return "\n".join(output)

@mcp.tool()
def search_legal_terms(query: str) -> str:
    """
    Search for legal terms (definitions).
    Returns a list of matching terms with IDs.
    """
    logger.info(f"Searching legal terms: {query}")
    data = client.get_legal_term_list(query)
    
    if 'LawTermSearch' not in data or 'lawTerm' not in data['LawTermSearch']:
        return "No legal terms found."
        
    items = data['LawTermSearch']['lawTerm']
    if not isinstance(items, list): items = [items]
    
    output = [f"# Legal Term Search Results for '{query}'", ""]
    for item in items:
        name = item.get('법령용어명', 'Unknown')
        id = item.get('법령용어일련번호', '') # MST ID
        desc = item.get('법령용어내용', '') # Brief
        source = item.get('출처법령명', '')
        output.append(f"- **{name}** (Source: {source}) [ID: term:{id}]")
        
    return "\n".join(output)

@mcp.tool()
def search_statutory_interpretations(query: str) -> str:
    """
    Search for statutory interpretations (authoritative interpretations by Ministry of Government Legislation).
    """
    logger.info(f"Searching interpretations: {query}")
    data = client.get_statutory_interpretation_list(query)
    
    if 'Expc' not in data or 'expc' not in data['Expc']:
        return "No interpretations found."
        
    items = data['Expc']['expc']
    if not isinstance(items, list): items = [items]
    
    output = [f"# Statutory Interpretation Search Results for '{query}'", ""]
    for item in items:
        title = item.get('안건명', 'Unknown')
        no = item.get('안건번호', '')
        date = item.get('회신일자', '')
        id = item.get('법령해석일련번호', '')
        output.append(f"- **{title}** (No: {no}, Date: {date}) [ID: interp:{id}]")
        
    return "\n".join(output)

@mcp.tool()
def get_statute_attachments(law_id: str) -> str:
    """
    Get a list of attached forms and tables (별표/서식) for a specific statute.
    Args:
        law_id: The ID of the law (e.g. "12345" or "statute:12345")
    """
    if ":" in law_id: law_id = law_id.split(":")[-1]
    logger.info(f"Getting attachments for law: {law_id}")
    
    data = client.get_law_detail(law_id)
    if '법령' not in data: return "Error: Law not found."
    
    law_info = data['법령']
    name = law_info.get('기본정보', {}).get('법령명_한글', 'Unknown')
    
    # Parse images/files (Byulpyo / Seosik)
    attachments = []
    
    # 1. Check for '별표' (Tables/Appendices)
    if '별표' in law_info:
        items = law_info['별표']
        if not isinstance(items, list): items = [items]
        for item in items:
            no = item.get('별표번호', '')
            title = item.get('별표제목', '')
            attachments.append(f"[별표 {no}] {title}")
            
    # 2. Check for '서식' (Forms)
    if '서식' in law_info:
        items = law_info['서식']
        if not isinstance(items, list): items = [items]
        for item in items:
            no = item.get('서식번호', '')
            title = item.get('서식제목', '')
            attachments.append(f"[서식 {no}] {title}")

    if not attachments:
        return f"# {name}\n\nNo attached forms or tables found."
        
    output = [f"# {name} - Attached Files", ""]
    output.extend(attachments)
    output.append("")
    output.append("Note: Direct file downloads are not yet supported via text response,")
    output.append("but these exist in the official record.")
    
    return "\n".join(output)


@mcp.tool()
def read_legal_resource(resource_id: str) -> str:
    """
    Reads the full content of a specific legal resource using its Typed ID.
    
    Args:
        resource_id: A string strictly in the format `type:id` (e.g., "statute:12345", "prec:98765", "admrul:54321").
                     The ID is obtained from the `search_korean_law` output.

    Features:
    - **Full Text Retrieval**: Fetches the complete text of statutes, precedents, or rules.
    - **Reference Resolution**: Automatically detects references to other laws (e.g., "refer to Article 5") within the text
      and appends their content to the response, saving you extra round-trips.
    - **Robustness**: Automatically handles ID formatting issues or outdated IDs by trying fallbacks (ID -> MST -> Detc).

    Return:
    - Markdown formatted text containing the resource metadata, body content, and resolved references.
    """
    logger.info(f"Reading resource: {resource_id}")
    
    try:
        if ":" not in resource_id:
            return "Error: Invalid ID format. Expected 'type:id' (e.g. statute:12345)."
            
        r_type, r_id = resource_id.split(":", 1)
        
        content = ""
        
        if r_type == "statute":
            content = get_statute_detail_internal(r_id)
            
        elif r_type == "prec":
            content = get_precedent_detail_internal(r_id)
            
        elif r_type == "admrul":
            content = get_admin_rule_detail_internal(r_id)
            
        elif r_type == "const":
            content = get_prec_const_detail_internal(r_id)
            
        elif r_type == "ordin":
            content = get_autonomous_law_detail_internal(r_id)
            
        elif r_type == "term":
            content = get_legal_term_detail_internal(r_id)
            
        elif r_type == "interp":
            content = get_statutory_interpretation_detail_internal(r_id)
            
        else:
            return f"Error: Unknown resource type '{r_type}'."
            
        # Auto-resolve references for statutes and maybe others
        # We only resolve if content was successfully retrieved
        if content and not content.startswith("Error"):
             refs = resolve_references(content)
             if "No specific cross-references" not in refs:
                 content += "\n\n" + refs
                 
        return content
            
        return content
            
    except Exception as e:
        return f"Error reading resource: {e}"

@mcp.tool()
def explore_legal_chain(query: str) -> str:
    """
    Perform a 'Deep Search' (Legal Graph).
    Use this when you want to understand the full context of a law provision, including:
    1. The provision itself.
    2. Other articles it refers to ("Internal/External References").
    3. Detailed regulations that define its scope ("Presidential Decree").
    
    Usage:
    - "Higher Education Act Article 20"
    - "고등교육법 제20조"
    
    Returns:
    - A comprehensive markdown document containing the main article and all connected legal texts.
    """
    from .utils import smart_search_statute_internal, client, _parse_articles, resolve_references, resolve_delegation
    
    logger.info(f"Exploring legal chain for: {query}")
    
    # 1. Resolve Target Law & Article
    # We reuse smart_search logic but we need the raw ID and Article No to be precise.
    # So we'll parse the query here manually akin to utils logic or just rely on search.
    
    # Parse query
    # Pattern 1: "LawName Je 20 jo" or "LawNameJe20jo" (Explicit 'Je')
    match = re.search(r'(.+?)\s*제\s*(\d+)조', query)
    if not match:
        # Pattern 2: "LawName 20 jo" (No 'Je', must have space)
        match = re.search(r'(.+?)\s+(\d+)조', query)
    
    if not match:
         match_en = re.search(r'(.*?)\s*(?:Article|Art\.?)\s*(\d+)', query, re.IGNORECASE)
         if match_en:
             law_query = match_en.group(1).strip()
             art_no = match_en.group(2)
         else:
             return "Please provide a specific article, e.g., '고등교육법 제20조' or 'Civil Act Article 5'."
    else:
        law_query = match.group(1).strip()
        art_no = match.group(2)

    # Search Law ID
    data = client.search_law(law_query)
    if 'LawSearch' not in data or 'law' not in data['LawSearch']:
         return f"Could not find law: {law_query}"
         
    items = data['LawSearch']['law']
    if not isinstance(items, list): items = [items]
    target_law = items[0] # Best guess
    law_id = target_law.get('법령일련번호')
    law_name = target_law.get('법령명한글')
    
    # 2. Get Main Article Content
    from .utils import get_statute_article_internal
    main_text = get_statute_article_internal(law_id, art_no)
    
    if "not found" in main_text: return main_text
    
    # 3. Resolve References
    output = [f"# Legal Chain Analysis: {law_name} Article {art_no}\n"]
    output.append("## 1. Main Provision")
    output.append(main_text)
    
    # Internal/External Refs
    refs = resolve_references(main_text, context_law_name=law_name, context_law_id=law_id)
    if refs:
        output.append("\n" + refs)
        
    # Delegations (Act -> Decree)
    delegations = resolve_delegation(main_text, context_law_name=law_name, context_law_id=law_id, current_article_no=art_no)
    if delegations:
        output.append(delegations)
        
    return "\n".join(output)
