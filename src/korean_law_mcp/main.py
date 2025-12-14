from mcp.server.fastmcp import FastMCP
from .api_client import KoreanLawClient
import logging
import os
import re
import concurrent.futures
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("korean-law-mcp")

# Initialize FastMCP
mcp = FastMCP("Korean Law MCP")
client = KoreanLawClient()

# --- Resources ---
@mcp.resource("law://statute/{id}")
def read_statute_resource(id: str) -> str:
    """Read full text of a statute (Law)"""
    logger.info(f"Reading statute resource: {id}")
    return get_statute_detail_internal(id)

@mcp.resource("law://statute/{id}/art/{art_no}")
def read_statute_article_resource(id: str, art_no: str) -> str:
    """Read a specific article from a statute"""
    logger.info(f"Reading statute article: {id} Art {art_no}")
    return get_statute_article_internal(id, art_no)

@mcp.resource("law://prec/{id}")
def read_precedent_resource(id: str) -> str:
    """Read content of a precedent (Case Law)"""
    logger.info(f"Reading precedent resource: {id}")
    return get_precedent_detail_internal(id)

@mcp.resource("law://admrul/{id}")
def read_admrul_resource(id: str) -> str:
    """Read content of an administrative rule"""
    logger.info(f"Reading admin rule resource: {id}")
    return get_admin_rule_detail_internal(id)


# --- Prompts ---
@mcp.prompt()
def summarize_law(law_id: str) -> list[types.PromptMessage]:
    """
    Create a prompt to summarize a specific law.
    Fetches the full text of the law and asks the LLM to summarize it.
    """
    law_text = get_statute_detail_internal(law_id)
    return [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"다음 법령(ID: {law_id})의 내용을 바탕으로 주요 조항, 입법 취지, 그리고 핵심 구조를 요약해 주세요.\\n\\n[법령 내용]\\n{law_text}"
            )
        )
    ]

@mcp.prompt()
def explain_legal_term(term: str) -> list[types.PromptMessage]:
    """
    Create a prompt to explain a legal term based on search results.
    Performs a smart search for the term and provides the results as context.
    """
    # Reuse the smart search logic. We can call the tool function directly.
    search_results = search_korean_law(term)
    return [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"다음은 '{term}'에 대한 한국 법령 및 판례 검색 결과입니다. 이 정보를 바탕으로 해당 법률 용어의 의미와 맥락을 설명해 주세요.\\n\\n[검색 결과]\\n{search_results}"
            )
        )
    ]

@mcp.prompt()
def compare_laws(law_id_1: str, law_id_2: str) -> list[types.PromptMessage]:
    """
    Create a prompt to compare two laws or articles.
    Fetches both resources and asks for a comparison.
    """
    text1 = get_statute_detail_internal(law_id_1)
    # If the user passed an Article ID pattern (though this generic fetcher might fail for article-specific patterns if not handled), 
    # for now we assume law_id. 
    # To support article comparison, we might need a smarter fetcher or just fetch full law.
    # Let's stick to law comparison for now.
    text2 = get_statute_detail_internal(law_id_2)
    
    return [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"다음 두 법령(조문)을 비교 분석해 주세요. 차이점과 유사점, 그리고 법적 효력의 차이를 중점으로 설명해 주세요.\\n\\n[법령 1 (ID: {law_id_1})]\\n{text1}\\n\\n[법령 2 (ID: {law_id_2})]\\n{text2}"
            )
        )
    ]


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
        # Note: "Law 10" simple regex might match "Budget 2024". 
        # But smart_search_statute_internal validates if it's a law. 
        # Low risk of false positive leading to bad error (just "not found").
        return smart_search_statute_internal(query)
    
    # 2. Otherwise default to integrated search
    return search_integrated_internal(query)

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
            
        else:
            return f"Error: Unknown resource type '{r_type}'."
            
        # Auto-resolve references for statutes and maybe others
        # We only resolve if content was successfully retrieved
        if content and not content.startswith("Error"):
             refs = resolve_references(content)
             if "No specific cross-references" not in refs:
                 content += "\n\n" + refs
                 
        return content
            
    except Exception as e:
        return f"Error reading resource: {e}"

# --- Internal Implementations (Migrated from Tools) ---

def search_statute_internal(query: str) -> str:
    # Original search_statute logic
    logger.info(f"Searching for: {query}")
    data = client.search_law(query)
    if 'LawSearch' not in data or 'law' not in data['LawSearch']:
        return "No results found."
    laws = data['LawSearch']['law']
    if not isinstance(laws, list): laws = [laws]
    output = []
    for law in laws:
        name = law.get('법령명한글', 'Unknown')
        id = law.get('법령일련번호', 'Unknown') 
        date = law.get('공포일자', 'Unknown')
        output.append(f"ID: statute:{id} | Name: {name} | Date: {date}")
    return "\n".join(output)

def get_statute_detail_internal(law_id: str) -> str:
    logger.info(f"Getting details for ID: {law_id}")
    data = client.get_law_detail(law_id)
    if '법령' not in data: return "Error: Law not found."
    law_info = data['법령']
    name = law_info.get('기본정보', {}).get('법령명_한글', 'Unknown')
    parsed_articles = _parse_articles(law_info)
    if not parsed_articles: return f"# {name}\n\n(No articles found)"
    articles_text = [a['full_text'] for a in parsed_articles]
    return f"# {name}\n\n" + "\n".join(articles_text)

def get_precedent_detail_internal(prec_id: str) -> str:
    logger.info(f"Getting precedent details for ID: {prec_id}")
    data = client.get_precedent_detail(prec_id)
    
    if 'PrecService' not in data:
        # Fallback: Try with MST parameter
        # Some older precedents or specific IDs require MST instead of ID
        logger.info(f"Standard fetch failed for {prec_id}. Trying MST fallback...")
        try:
            import requests
            import xmltodict
            url = f"{client.BASE_URL}/DRF/lawService.do"
            params = {
                "OC": client.user_id,
                "target": "prec",
                "type": "XML",
                "MST": prec_id 
            }
            resp = requests.get(url, params=params)
            data = xmltodict.parse(resp.content)
        except Exception as e:
            logger.error(f"MST fallback failed: {e}")
    
    if 'PrecService' not in data:
        # Fallback: Try with MST parameter
        logger.info(f"Standard fetch failed (ID={prec_id}). Trying MST fallback...")
        try:
            import requests
            import xmltodict
            url = f"{client.BASE_URL}/DRF/lawService.do"
            params = {
                "OC": client.user_id,
                "target": "prec",
                "type": "XML",
                "MST": prec_id 
            }
            resp = requests.get(url, params=params)
            data = xmltodict.parse(resp.content)
        except Exception as e:
            logger.error(f"MST fallback failed: {e}")
            
    if 'PrecService' not in data:
        # Final Fallback: Check if it's actually a Constitutional Court decision (target='detc')
        # Sometimes 'prec' search returns const court cases but they must be fetched via 'detc'.
        logger.info(f"Prec fetch failed. Checking if ID={prec_id} is a Constitutional Court decision...")
        detc_content = get_prec_const_detail_internal(prec_id)
        if "Error" not in detc_content[:20]:
            return detc_content
            
        return "Error: Law/Precedent not found or Invalid ID. (Tried ID, MST, and Detc conversion)"
        
    info = data['PrecService']
    title = info.get('사건명', 'Unknown')
    case_no = info.get('사건번호', 'Unknown')
    date = info.get('선고일자', 'Unknown')
    court = info.get('법원명', 'Unknown')
    summary = info.get('판결요지', '')
    content = info.get('판례내용', '')
    holding = info.get('판시사항', '')
    
    def clean_html(text):
        if not text: return ""
        text = text.replace("<br/>", "\n").replace("&lt;", "<").replace("&gt;", ">")
        return text.strip()
        
    output = [
        f"# {title}",
        f"**Case No:** {case_no}",
        f"**Court:** {court}",
        f"**Date:** {date}",
        "",
        "## 판시사항 (Holding)",
        clean_html(holding),
        "",
        "## 판결요지 (Summary)",
        clean_html(summary),
        "",
        "## 판례내용 (Full Text)",
        clean_html(content)
    ]
    return "\n".join(output)

def get_admin_rule_detail_internal(adm_id: str) -> str:
    logger.info(f"Getting admin rule details for ID: {adm_id}")
    data = client.get_admin_rule_detail(adm_id)
    if 'AdmRulService' not in data: return "Error: Invalid response structure (Missing 'AdmRulService')"
    root = data['AdmRulService']
    info = root.get('행정규칙기본정보', {})
    name = info.get('행정규칙명', 'Unknown')
    dept = info.get('소관부처명', '')
    
    content_acc = []
    def clean_html(text):
        if not text: return ""
        text = str(text)
        text = text.replace("<br/>", "\n").replace("&lt;", "<").replace("&gt;", ">")
        return text.strip()

    if '조문내용' in root:
        content = root['조문내용']
        if isinstance(content, str): content_acc.append(clean_html(content))
        elif isinstance(content, list):
             for c in content: content_acc.append(clean_html(str(c)))
    
    if not content_acc:
        full_text = root.get('전문', '')
        if full_text: content_acc.append(clean_html(full_text))
            
    if not content_acc:
        buchik = root.get('부칙')
        if buchik: content_acc.append("\n[부칙]\n" + clean_html(str(buchik)))
        else: content_acc.append("(No content found.)")
        
    return f"# {name} ({dept})\n\n" + "\n".join(content_acc)

def get_prec_const_detail_internal(detc_id: str) -> str:
    logger.info(f"Getting const. decision details for ID: {detc_id}")
    data = client.get_prec_const_detail(detc_id)
    if 'DetcService' not in data: return "Error: Invalid response structure (Missing 'DetcService')"
    info = data['DetcService']
    title = info.get('사건명', 'Unknown')
    case_no = info.get('사건번호', 'Unknown')
    date = info.get('종국일자', 'Unknown')
    type_name = info.get('사건종류명', '')
    holding = info.get('판시사항', '')
    summary = info.get('결정요지', '')
    content = info.get('전문', '')
    
    def clean_html(text):
        if not text: return ""
        text = str(text)
        text = text.replace("<br/>", "\n").replace("&lt;", "<").replace("&gt;", ">")
        text = text.replace("<![CDATA[", "").replace("]]>", "")
        return text.strip()
        
    output = [
        f"# {title}",
        f"**Case No:** {case_no}",
        f"**Type:** {type_name}",
        f"**Date:** {date}",
        "",
        "## 판시사항 (Holding)",
        clean_html(holding),
        "",
        "## 결정요지 (Summary)",
        clean_html(summary),
        "",
        "## 전문 (Full Text)",
        clean_html(content)
    ]
    return "\n".join(output)

def get_autonomous_law_detail_internal(law_id: str) -> str:
    logger.info(f"Getting autonomous law details for ID: {law_id}")
    data = client.get_autonomous_law_detail(law_id)
    if 'LawService' not in data: return "Error: Invalid response structure (Missing 'LawService')"
    
    root = data['LawService']
    info = root.get('자치법규기본정보', {})
    name = info.get('자치법규명', 'Unknown')
    gov = info.get('지자체기관명', '')
    
    articles = []
    jomun_section = root.get('조문', {})
    if jomun_section:
        body = jomun_section.get('조문단위') or jomun_section.get('조') or []
        if not isinstance(body, list): body = [body]
        for item in body:
            content = item.get('조문내용') or item.get('조내용') or ''
            content = content.strip()
            if not content and '#text' in item: content = item['#text'].strip()
            no = item.get('조문번호', '?')
            title = item.get('조문제목') or item.get('조제목') or ''
            header = f"제{no}조({title})" if title else f"제{no}조"
            articles.append(f"{header}: {content}")
            if '항' in item:
                paragraphs = item['항']
                if not isinstance(paragraphs, list): paragraphs = [paragraphs]
                for p in paragraphs:
                    p_content = p.get('항내용', '').strip()
                    p_no = p.get('항번호', '')
                    if p_content: articles.append(f"  {p_no}. {p_content}")
    if not articles: articles.append("(No parsed articles found. The law might use a different structure or be empty.)")
    return f"# {name} ({gov})\n\n" + "\n".join(articles)

def _parse_articles(law_info: dict) -> list[dict]:
    """
    Helper to parse articles from law info dictionary.
    Returns a list of dicts: {'no': str, 'title': str, 'full_text': str}
    """
    articles = []
    # Articles are in '조문' -> '조문단위'
    try:
        jomun_section = law_info.get('조문', {})
        if not jomun_section:
            return []

        body = jomun_section.get('조문단위', [])
        if not isinstance(body, list):
            body = [body]
            
        for item in body:
            # Check for '조문내용' (Article Content)
            content = item.get('조문내용', '')
            # If empty, sometimes content is in text node or formatted differently
            if not content and '#text' in item:
                content = item['#text']
            
            content = content.strip()
            
            article_no = item.get('조문번호', '?')
            title = item.get('조문제목', '')
            
            full_text_lines = []
            
            if title:
                header_text = f"제{article_no}조({title})"
            else:
                header_text = f"제{article_no}조"
            
            # Prevent duplication if content already starts with the header
            # Normalize spaces for comparison
            normalized_content = content.replace(" ", "")
            normalized_header = header_text.replace(" ", "")
            
            if normalized_content.startswith(normalized_header):
                # formatting: "Title: Title content..."
                # If content is exactly the header, maybe it's just a title line?
                # We'll just use the content as is, but often we want to format it nicely.
                # If we prepended header, it would be "Title: Title content..." -> Duplicate.
                # So we just use content.
                full_text_lines.append(content)
            else:
                full_text_lines.append(f"{header_text}: {content}")
            
            # Sub-paragraphs (항)
            paragraphs = item.get('항', [])
            if not isinstance(paragraphs, list):
                paragraphs = [paragraphs]
            
            for p in paragraphs:
                p_content = p.get('항내용', '').strip()
                p_no = p.get('항번호', '')
                if p_content:
                    # Sometimes p_content also starts with p_no (e.g. "① Text")
                    if p_content.startswith(p_no):
                        full_text_lines.append(f"  {p_content}")
                    else:
                        full_text_lines.append(f"  {p_no}. {p_content}")
                    
                # Sub-sub-paragraphs (호) are inside '항' -> '호'
                hos = p.get('호', [])
                if not isinstance(hos, list):
                    hos = [hos]
                for h in hos:
                    h_content = h.get('호번호', '') + " " + h.get('호내용', '').strip()
                    h_content = h_content.strip()
                    full_text_lines.append(f"    {h_content}")
            
            # Deduplicate items in TOC generation
            # We can't easily dedupe here, but we can ensure we don't produce empty entries
            
            # Extract '조문여부' to distinguish between headers ("전문") and content ("조문")
            art_type = item.get('조문여부', '')
            
            articles.append({
                'no': str(article_no),
                'title': title,
                'full_text': "\n".join(full_text_lines),
                'type': art_type
            })

    except Exception as e:
        logger.error(f"Error parsing articles: {e}")
        return []
        
    return articles

def get_statute_article_internal(law_id: str, article_no: str) -> str:
    """
    Get the full text of a specific article from a statute.
    Args:
        law_id: The ID of the law (from search_statute).
        article_no: The article number (e.g., "20", "20-2").
    """
    logger.info(f"Getting article {article_no} for law ID: {law_id}")
    data = client.get_law_detail(law_id)
    
    if '법령' not in data:
        return "Error: Invalid response structure (Missing '법령')"
        
    law_info = data['법령']
    name = law_info.get('기본정보', {}).get('법령명_한글', 'Unknown')
    
    parsed_articles = _parse_articles(law_info)
    
    for art in parsed_articles:
        if art['no'] == article_no:
            # If we find a content article, return immediately. 
            # If we find a header, store it but keep looking.
            if art.get('type') == '조문':
                return f"# {name} 제{article_no}조\n\n" + art['full_text']
            
            # If we haven't found a content article yet, maybe this header is the best we got?
            # But usually we want to keep looking.
            pass
            
    # Second pass: if we are here, we didn't find "조문". Return the first match (header) if any.
    for art in parsed_articles:
        if art['no'] == article_no:
             return f"# {name} 제{article_no}조\n\n" + art['full_text']

    return f"Article {article_no} not found in {name}."

def smart_search_statute_internal(query: str) -> str:
    # Logic from previous smart_search_statute
    logger.info(f"Smart searching for: {query}")
    article_no = None
    
    # 1. Pattern: "제103조" or "제 103 조"
    kr_match = re.search(r'제\s*(\d+(?:의\d+)?)', query)
    
    # 2. Pattern: "Article 103"
    en_match = re.search(r'(?:Article|Art\.?)\s*(\d+(?:-\d+)?)', query, re.IGNORECASE)
    
    # 3. Pattern: "LawName 103" (Relaxed, end of string or space boundary)
    # e.g. "민법 103", "Civil Act 103"
    # We look for a number at the end of the query or preceded by space
    relaxed_match = re.search(r'(?:\s|^)(\d+(?:-\d+)?)(?:\s|$)', query)

    if kr_match:
        article_no = kr_match.group(1)
        clean_query = re.sub(r'제\s*(\d+(?:의\d+)?)', '', query).strip()
        # Remove trailing '조' if valid
        clean_query = clean_query.replace('조', '').strip()
    elif en_match:
        article_no = en_match.group(1)
        clean_query = re.sub(r'(?:Article|Art\.?)\s*(\d+(?:-\d+)?)', '', query, flags=re.IGNORECASE).strip()
    elif relaxed_match:
         # Only trigger if the query *starts* with text (Law name)
         # and the number is independent.
         candidate_no = relaxed_match.group(1)
         # Verify it's not part of the law name (simple heuristic)
         start, end = relaxed_match.span(1)
         # If simpler query remains
         clean_query = (query[:start] + query[end:]).strip()
         if clean_query:
             article_no = candidate_no
         else:
             clean_query = query
    else:
        clean_query = query
            
    clean_query = re.sub(r'\bof\b', '', clean_query, flags=re.IGNORECASE).strip()
    data = client.search_law(clean_query)
    if 'LawSearch' not in data or 'law' not in data['LawSearch']:
        return f"No laws found for query: '{clean_query}'"
    items = data['LawSearch']['law']
    if not isinstance(items, list): items = [items]
    
    best_match = None
    exact_matches = [i for i in items if i.get('법령명한글', '').replace(' ', '') == clean_query.replace(' ', '')]
    statute_matches = [i for i in items if i.get('법령구분명') == '법률']
    
    if exact_matches:
        best_match = exact_matches[0]
        for m in exact_matches:
            if m.get('현행연혁코드') == '현행':
                best_match = m
                break
    elif statute_matches: best_match = statute_matches[0]
    else: best_match = items[0]
        
    law_name = best_match.get('법령명한글', 'Unknown')
    law_id = best_match.get('법령일련번호')
    if not law_id: return "Error: Selected law has no ID."
    
    logger.info(f"Selected law: {law_name} ({law_id})")
    detail_data = client.get_law_detail(law_id)
    if '법령' not in detail_data: return "Error: Could not retrieve law details."
    law_info = detail_data['법령']
    parsed_articles = _parse_articles(law_info)
    
    if article_no:
        # Priority Search for Content
        for art in parsed_articles:
            if art['no'] == article_no and art.get('type') == '조문':
                return f"# {law_name} 제{article_no}조\n\n{art['full_text']}"
        
        # Fallback to any match
        for art in parsed_articles:
             if art['no'] == article_no:
                return f"# {law_name} 제{article_no}조\n\n{art['full_text']}"
                
        return f"Article {article_no} not found in {law_name}."
    else:
        output = [f"# {law_name}"]
        enforce_date = law_info.get('기본정보', {}).get('시행일자', '')
        output.append(f"Enforcement Date: {enforce_date}")
        output.append("")
        output.append("## Table of Contents (First 30 Articles)")
        last_no = None
        count = 0
        for art in parsed_articles:
            if art['no'] == last_no and not art['title']: continue
            display_title = art['title'] if art['title'] else "(No Title)"
            output.append(f"- 제{art['no']}조: {display_title}")
            last_no = art['no']
            count += 1
            if count >= 30:
                output.append(f"... and {len(parsed_articles) - 30} more articles.")
                break
        output.append("")
        output.append("To read a specific article, try searching 'LawName Article X'.")
        return "\n".join(output)

def search_integrated_internal(query: str) -> str:
    logger.info(f"Integrated search for: {query}")
    results = {}
    def search_target(target, label):
        try:
            res = client.search_law(query, target=target)
            return label, res
        except Exception as e:
            logger.error(f"Error searching {label}: {e}")
            return label, None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(search_target, "law", "Statutes"),
            executor.submit(search_target, "prec", "Precedents"),
            executor.submit(search_target, "admrul", "AdminRules")
        ]
        for future in concurrent.futures.as_completed(futures):
            label, res = future.result()
            results[label] = res
            
    output = [f"# Integrated Search Results for '{query}'\n"]
    
    statutes = results.get("Statutes", {})
    output.append("## 1. Statutes (법령)")
    if statutes and 'LawSearch' in statutes and 'law' in statutes['LawSearch']:
        items = statutes['LawSearch']['law']
        if not isinstance(items, list): items = [items]
        for item in items[:3]:
            name = item.get('법령명한글', '')
            id = item.get('법령일련번호', '')
            date = item.get('시행일자', '')
            output.append(f"- **{name}** (Date: {date}) [ID: statute:{id}]")
    else: output.append("(No results)")
    output.append("")
        
    precs = results.get("Precedents", {})
    output.append("## 2. Precedents (판례)")
    if precs and 'PrecSearch' in precs and 'prec' in precs['PrecSearch']:
        items = precs['PrecSearch']['prec']
        if not isinstance(items, list): items = [items]
        for item in items[:3]:
            name = item.get('사건명', '')
            case_no = item.get('사건번호', '')
            id = item.get('판례일련번호', '')
            output.append(f"- **{case_no} {name}** [ID: prec:{id}]")
    else: output.append("(No results)")
    output.append("")

    rules = results.get("AdminRules", {})
    output.append("## 3. Administrative Rules (행정규칙)")
    if rules and 'AdmRulSearch' in rules and 'admrul' in rules['AdmRulSearch']:
        items = rules['AdmRulSearch']['admrul']
        if not isinstance(items, list): items = [items]
        for item in items[:3]:
            name = item.get('행정규칙명', '')
            id = item.get('행정규칙일련번호', '')
            dept = item.get('소관부처명', '')
            output.append(f"- **{name}** ({dept}) [ID: admrul:{id}]")
    else: output.append("(No results)")
    return "\n".join(output)


def resolve_references(content: str) -> str:
    """
    Analyze the provided legal text (e.g., an article content), identify references to other laws/articles,
    and attempt to fetch basic info or summaries for them.
    
    Currently supports:
    - References to "Article X" within the same law (context needed, but we'll try best guess or just highlight).
    - References to specific laws by name (e.g. "Higher Education Act").
    
    For now, this tool will just extract potential references and suggest searches, 
    as full resolution requires passing the parent Law ID to be accurate about "Article X".
    
    Refined Behavior:
    - Parses "XX법 제YY조" (Law XX Article YY).
    - Fetches the referenced Article YY of Law XX.
    """
    logger.info("Resolving references...")
    
    # Regex for "XX법 제YY조"
    # This is tricky because "XX법" can be anything.
    # We'll look for pattern: ([가-힣]+법)\s*제(\d+)조
    
    pattern = r'([가-힣]+법)\s*제(\d+)조'
    matches = re.findall(pattern, content)
    
    if not matches:
        return "No specific cross-references (Link to Law + Article) found in the text."
        
    output = ["# Referenced Articles Resolution\n"]
    
    # Deduplicate
    unique_matches = list(set(matches))
    
    # Limit resolution to avoiding spamming API
    if len(unique_matches) > 3:
        output.append(f"(Found {len(unique_matches)} references. Showing top 3.)\n")
        unique_matches = unique_matches[:3]
        
    for law_name, art_no in unique_matches:
        output.append(f"## {law_name} Article {art_no}")
        
        # 1. Find the law ID
        try:
            # Re-use smart search logic slightly manually
            # We want exact match for law name
            search_res = client.search_law(law_name)
            if 'LawSearch' in search_res and 'law' in search_res['LawSearch']:
                items = search_res['LawSearch']['law']
                if not isinstance(items, list): items = [items]
                
                # Find exact match
                target_law = None
                for i in items:
                    if i.get('법령명한글', '').replace(' ', '') == law_name.replace(' ', ''):
                        target_law = i
                        break
                
                if not target_law and items:
                    target_law = items[0] # Fallback
                
                if target_law:
                    law_id = target_law.get('법령일련번호')
                    
                    # 2. Get Article
                    art_text = get_statute_article_internal(law_id, art_no)
                    output.append(art_text)
                else:
                    output.append(f"Could not find law ID for '{law_name}'.")
            else:
                output.append(f"Law '{law_name}' not found.")
                
        except Exception as e:
            output.append(f"Error resolving: {e}")
            
        output.append("---")
        
    return "\n".join(output)

def main():
    mcp.run()

if __name__ == "__main__":
    main()

