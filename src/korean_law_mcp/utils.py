import logging
import re
import concurrent.futures
import xmltodict
import requests
from .api_client import KoreanLawClient

# Configure logging
logger = logging.getLogger("korean-law-mcp")

# Initialize Client
client = KoreanLawClient()

# --- Helpers ---

def clean_html(text):
    if not text: return ""
    text = str(text)
    text = text.replace("<br/>", "\n").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("<![CDATA[", "").replace("]]>", "")
    return text.strip()

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

# --- Internal Implementations ---

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

def get_precedent_detail_internal(prec_id: str) -> str:
    logger.info(f"Getting precedent details for ID: {prec_id}")
    data = client.get_precedent_detail(prec_id)
    
    if 'PrecService' not in data:
        # Fallback: Try with MST parameter
        # Some older precedents or specific IDs require MST instead of ID
        logger.info(f"Standard fetch failed for {prec_id}. Trying MST fallback...")
        try:
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
        # Fallback: Try with MST parameter again (Redundant block in original, but keeping logic safe)
        logger.info(f"Standard fetch failed (ID={prec_id}). Trying MST fallback...")
        # (Skipping duplicate try-except block, assuming previous one covered it or intention was retry)
        # Actually in original code it was duplicated. I'll just check once effectively.
        pass
            
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
    
    # --- Knowledge Graph: Relationships ---
    ref_articles = info.get('참조조문', '')
    ref_cases = info.get('참조판례', '')

    output = [
        f"# {title}",
        f"**Case No:** {case_no}",
        f"**Court:** {court}",
        f"**Date:** {date}",
        f"**ID:** {prec_id}",
        "",
        "## 판시사항 (Holding)",
        clean_html(holding),
        "",
        "## 판결요지 (Summary)",
        clean_html(summary),
        "",
        "## 전문 (Full Text)",
        clean_html(content)
    ]
    
    # Append Knowledge Graph Links
    if ref_articles or ref_cases:
        output.append("")
        output.append("## 참조 정보 (Related Resources)")
        if ref_articles:
            output.append(f"### 참조 조문 (Referenced Articles)\n{clean_html(ref_articles)}")
        if ref_cases:
            output.append(f"### 참조 판례 (Referenced Cases)\n{clean_html(ref_cases)}")
            
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
    summary = info.get('결정요지', '') # Constitutional Court uses 결정요지
    content = info.get('전문', '') # Constitutional Court uses 전문
    
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

def get_legal_term_detail_internal(term_id: str) -> str:
    logger.info(f"Getting legal term details for ID: {term_id}")
    data = client.get_legal_term_detail(term_id)
    
    if 'LawTermService' not in data: return "Error: Law Term not found."
    
    info = data['LawTermService']
    name = info.get('법령용어명', 'Unknown')
    desc = info.get('법령용어내용', '') # Definition
    source = info.get('출처법령명', '')
    
    # Search metadata like which article defines it
    article_ref = info.get('용어정의조문', '') # Sometimes present
    
    return f"# {name}\n\n**Source:** {source}\n**Ref:** {article_ref}\n\n## Definition\n{desc}"

def get_statutory_interpretation_detail_internal(interp_id: str) -> str:
    logger.info(f"Getting interpretation details for ID: {interp_id}")
    data = client.get_statutory_interpretation_detail(interp_id)
    
    if 'ExpcService' not in data: return "Error: Interpretation not found."
    
    info = data['ExpcService']
    title = info.get('안건명', 'Unknown')
    no = info.get('안건번호', '')
    date = info.get('회신일자', '')
    
    # Content fields
    question = info.get('질의요지', '')
    answer = info.get('회답', '')
    reason = info.get('이유', '')
    
    output = [
        f"# {title}",
        f"**Case No:** {no}",
        f"**Date:** {date}",
        "",
        "## 질의요지 (Question)",
        clean_html(question),
        "",
        "## 회답 (Answer)",
        clean_html(answer),
        "",
        "## 이유 (Reasoning)",
        clean_html(reason)
    ]
    
    return "\n".join(output)

def get_law_history_internal(law_id: str, article_no: str = None) -> str:
    """
    Get the revision history of a law.
    Since the lsHistory API is not available, we extract revision info from the main law data.
    """
    logger.info(f"Getting law history for ID: {law_id}")
    
    try:
        # Use the regular law detail API which contains revision info
        data = client.get_law_detail(law_id)
    except Exception as e:
        logger.error(f"Error fetching law detail: {e}")
        return f"Error: Failed to fetch law information. {e}"
    
    if '법령' not in data:
        return "Error: Law not found."
    
    law_info = data['법령']
    basic_info = law_info.get('기본정보', {})
    
    law_name = basic_info.get('법령명_한글', 'Unknown')
    enforcement_date = basic_info.get('시행일자', '')
    promulgation_date = basic_info.get('공포일자', '')
    promulgation_no = basic_info.get('공포번호', '')
    revision_type = basic_info.get('제개정구분', '')
    
    output = [f"# {law_name} 연혁 정보", ""]
    
    output.append("## 현행 법령 정보")
    output.append(f"- **제개정구분**: {revision_type}")
    output.append(f"- **시행일자**: {enforcement_date}")
    output.append(f"- **공포일자**: {promulgation_date}")
    output.append(f"- **공포번호**: {promulgation_no}")
    output.append("")
    
    # 개정문 (Amendment document)
    amend_doc = law_info.get('개정문', {})
    if amend_doc:
        amend_content = amend_doc.get('개정문내용', '')
        if amend_content:
            output.append("## 개정문")
            output.append(clean_html(amend_content)[:500])
            if len(amend_content) > 500:
                output.append("...")
            output.append("")
    
    # 제개정이유 (Reason for amendment)
    reason_doc = law_info.get('제개정이유', {})
    if reason_doc:
        reason_content = reason_doc.get('제개정이유내용', '')
        if reason_content:
            output.append("## 제개정이유")
            output.append(clean_html(reason_content)[:1000])
            if len(reason_content) > 1000:
                output.append("...")
            output.append("")
    
    output.append("> **Note**: 전체 연혁 정보는 [법령정보센터](https://www.law.go.kr)에서 확인할 수 있습니다.")
    
    return "\n".join(output)

def get_old_new_comparison_internal(law_id: str) -> str:
    """
    Get the old/new article comparison (신구조문대비) for a law.
    Since the lsOnC API is not available, we provide web links and amendment info.
    """
    logger.info(f"Getting old/new comparison for ID: {law_id}")
    
    # Use the regular law detail API to get amendment info
    try:
        data = client.get_law_detail(law_id)
    except Exception as e:
        logger.error(f"Error fetching law detail: {e}")
        return f"Error: Failed to fetch law information. {e}"
    
    if '법령' not in data:
        return "Error: Law not found."
    
    law_info = data['법령']
    basic_info = law_info.get('기본정보', {})
    
    law_name = basic_info.get('법령명_한글', 'Unknown')
    enforcement_date = basic_info.get('시행일자', '')
    revision_type = basic_info.get('제개정구분', '')
    
    output = [f"# {law_name} 신구조문대비", ""]
    
    # Amendment document contains the actual changes
    amend_doc = law_info.get('개정문', {})
    if amend_doc:
        amend_content = amend_doc.get('개정문내용', '')
        if amend_content:
            output.append("## 최근 개정 내용")
            output.append(f"- **제개정구분**: {revision_type}")
            output.append(f"- **시행일자**: {enforcement_date}")
            output.append("")
            output.append("### 개정문")
            output.append("```")
            # Clean and show the amendment content
            clean_content = clean_html(amend_content)
            output.append(clean_content[:2000])
            if len(clean_content) > 2000:
                output.append("...")
            output.append("```")
            output.append("")
    
    # Provide web link for detailed comparison
    output.append("## 📎 신구조문대비표 확인")
    output.append("")
    output.append("> **Note**: 상세한 신구조문대비표는 국가법령정보센터에서 확인할 수 있습니다.")
    output.append("")
    output.append(f"**[🔗 {law_name} 신구조문대비표 보기](https://www.law.go.kr/lsScLsComp.do?lsiSeq={law_id})**")
    output.append("")
    output.append("위 링크에서 조문별 변경 전/후 내용을 시각적으로 비교할 수 있습니다.")
    
    return "\n".join(output)

def resolve_references(content: str, context_law_name: str = None, context_law_id: str = None) -> str:
    """
    Analyze legal text to resolve:
    1. Internal References ("Article 5") - Uses context_law_id
    2. External References ("Article 10 of Building Act")
    3. Delegations ("Presidential Decree") - Finds linked Enforcement Decree
    
    Args:
        content: The text to analyze
        context_law_name: Name of the law the content belongs to (e.g. "Higher Education Act")
        context_law_id: ID of the law
    """
    logger.info(f"Resolving references (Context: {context_law_name})...")
    output = []
    
    # --- 1. explicit External References (XX Act Article YY) ---
    ext_pattern = r'([가-힣]+법)\s*제(\d+)조'
    ext_matches = list(set(re.findall(ext_pattern, content)))
    
    # --- 2. Internal References (Article YY) ---
    # Look for "Article YY" NOT preceded by a law name
    # We use a negative lookbehind or just simple parsing if we strictly exclude the external ones
    # Simplified regex: "제\d+조"
    int_pattern = r'(?<![가-힣])제(\d+)조' 
    int_matches = []
    if context_law_id:
        raw_int_matches = re.findall(int_pattern, content)
        # Filter out those that were part of external matches
        # This is a heuristic. Ideally we'd tokenize. 
        # For now, let's just collect them.
        for art_no in raw_int_matches:
            # Check if this "Article X" was captured as "Act Article X"
            is_external = False
            for ext_law, ext_art in ext_matches:
                 if ext_art == art_no and f"{ext_law} 제{ext_art}조" in content:
                     # This check is weak but acceptable for MVP
                     pass
            int_matches.append(art_no)
        int_matches = list(set(int_matches))

    # --- 3. Gather Content ---
    
    resolved_count = 0
    max_refs = 5
    
    # Resolve Internal
    for art_no in int_matches:
        if resolved_count >= max_refs: break
        # Avoid recursion if resolving the article itself
        # (Caller handles this, but good to be safe)
        if f"제{art_no}조" in content.split('\n')[0]: continue
        
        try:
            art_text = get_statute_article_internal(context_law_id, art_no)
            if "not found" not in art_text and "Error" not in art_text:
                output.append(f"### [Internal] Je{art_no}jo\n{art_text}")
                resolved_count += 1
        except Exception as e:
            logger.error(f"Internal ref error: {e}")

    # Resolve External
    for law_name, art_no in ext_matches:
        if resolved_count >= max_refs: break
        if context_law_name and law_name in context_law_name: continue # Skip self-reference if name matches
        
        try:
            # Search for law ID
            search_res = client.search_law(law_name)
            if 'LawSearch' in search_res and 'law' in search_res['LawSearch']:
                 items = search_res['LawSearch']['law']
                 if not isinstance(items, list): items = [items]
                 target_law = items[0] # Best guess
                 
                 ext_id = target_law.get('법령일련번호')
                 art_text = get_statute_article_internal(ext_id, art_no)
                 output.append(f"### [External] {law_name} Article {art_no}\n{art_text}")
                 resolved_count += 1
        except Exception as e:
             logger.error(f"External ref error: {e}")

    if not output:
        return ""
        
    final_output = ["## Referenced Articles"] + output
    return "\n\n".join(final_output)

def resolve_delegation(content: str, context_law_name: str, context_law_id: str, current_article_no: str) -> str:
    """
    If content mentions "Presidential Decree" (대통령령), find the corresponding Enforcement Decree article.
    Strategy:
    1. Identify target decree name: "X Act" -> "X Act Enforcement Decree"
    2. Search/Fetch that Decree.
    3. Look for articles in that Decree that reference "Act Article {current_article_no}"
       (e.g. "Pursuant to Article 20 of the Act")
    """
    if "대통령령" not in content and "국회규칙" not in content and "대법원규칙" not in content:
        return ""
        
    logger.info(f"Checking delegations for {context_law_name} Art {current_article_no}")
    
    # 1. Guess Decree Name
    # Usually: Law Name + " 시행령" (Enforcement Decree)
    # Caution: Some laws just change "Act" to "Act Enforcement Decree"
    # But appending " 시행령" is safe for search smarts usually
    target_decree_name = context_law_name + " 시행령"
    
    # 2. Find Decree ID
    deg_id = None
    try:
        data = client.search_law(target_decree_name)
        if 'LawSearch' in data and 'law' in data['LawSearch']:
            items = data['LawSearch']['law']
            if not isinstance(items, list): items = [items]
            # Precise match preferred
            for item in items:
                if item.get('법령명한글', '').replace(' ', '') == target_decree_name.replace(' ', ''):
                    deg_id = item.get('법령일련번호')
                    break
            if not deg_id and items: deg_id = items[0].get('법령일련번호')
    except Exception as e:
        logger.error(f"Delegation search error: {e}")
        return ""
        
    if not deg_id: return ""
    
    # 3. Scan Decree for Back-References
    # "법 제X조" where X is current_article_no
    target_ref_pattern = f"법 제{current_article_no}조"
    
    # We fetch ALL articles of the decree to scan them. 
    # This might be heavy if decree is huge, but necessary for accurate linking.
    decree_detail = client.get_law_detail(deg_id)
    if '법령' not in decree_detail: return ""
    
    decree_info = decree_detail['법령']
    real_decree_name = decree_info.get('기본정보', {}).get('법령명_한글', target_decree_name)
    parsed = _parse_articles(decree_info)
    
    matches = []
    for art in parsed:
        if target_ref_pattern in art['full_text']:
            matches.append(art)
            
    if not matches:
        return f"\n\n## Delegated Legislation ({real_decree_name})\n(No specific article found referencing Act Article {current_article_no}.)"
        
    output = [f"\n\n## Delegated Legislation ({real_decree_name})"]
    for m in matches:
        output.append(f"### Article {m['no']} ({m['title']})")
        output.append(m['full_text'])
    
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
         candidate_no = relaxed_match.group(1)
         start, end = relaxed_match.span(1)
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
