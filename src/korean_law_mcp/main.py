from mcp.server.fastmcp import FastMCP
from .api_client import KoreanLawClient
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("korean-law-mcp")

# Initialize FastMCP
mcp = FastMCP("Korean Law MCP")
client = KoreanLawClient()

@mcp.tool()
def search_statute(query: str) -> str:
    """
    Search for Korean statutes (법령) by query.
    Returns a list of matching laws with their IDs.
    """
    logger.info(f"Searching for: {query}")
    data = client.search_law(query)
    
    if 'LawSearch' not in data or 'law' not in data['LawSearch']:
        return "No results found."
        
    laws = data['LawSearch']['law']
    if not isinstance(laws, list):
        laws = [laws]
        
    output = []
    for law in laws:
        name = law.get('법령명한글', 'Unknown')
        # The API sometimes returns '법령일련번호' as the ID we need for details
        id = law.get('법령일련번호', 'Unknown') 
        date = law.get('공포일자', 'Unknown')
        output.append(f"ID: {id} | Name: {name} | Date: {date}")
        
    return "\n".join(output)

@mcp.tool()
def get_statute_detail(law_id: str) -> str:
    """
    Get the full text of a specific statute using its ID.
    User 'search_statute' first to find the ID.
    """
    logger.info(f"Getting details for ID: {law_id}")
    data = client.get_law_detail(law_id)
    
    # Root element is '법령' (Statute)
    if '법령' not in data:
        return "Error: Invalid response structure (Missing '법령')"
        
    law_info = data['법령']
    name = law_info.get('기본정보', {}).get('법령명_한글', 'Unknown')
    
    articles = []
    # Articles are in '조문' -> '조문단위'
    try:
        # '조문' might be missing if the law has no articles (unlikely)
        jomun_section = law_info.get('조문', {})
        if not jomun_section:
            return f"# {name}\n\n(No articles found)"

        body = jomun_section.get('조문단위', [])
        if not isinstance(body, list):
            body = [body]
            
        for item in body:
            # Check for '조문내용' (Article Content)
            content = item.get('조문내용', '')
            # If empty, sometimes content is in text node or formatted differently
            if not content and '#text' in item:
                content = item['#text']
            
            # Remove excessive whitespace
            content = content.strip()
            
            article_no = item.get('조문번호', '?')
            title = item.get('조문제목', '')
            
            if title:
                header = f"제{article_no}조({title})"
            else:
                header = f"제{article_no}조"
            
            articles.append(f"{header}: {content}")
            
            # Sub-paragraphs (항)
            paragraphs = item.get('항', [])
            if not isinstance(paragraphs, list):
                paragraphs = [paragraphs]
            
            for p in paragraphs:
                p_content = p.get('항내용', '').strip()
                p_no = p.get('항번호', '')
                if p_content:
                    articles.append(f"  {p_no}. {p_content}")
                    
                # Sub-sub-paragraphs (호) are inside '항' -> '호'
                hos = p.get('호', [])
                if not isinstance(hos, list):
                    hos = [hos]
                for h in hos:
                    h_content = h.get('호내용', '').strip()
                    h_no = h.get('호번호', '')
                    if h_content:
                        articles.append(f"    {h_no}. {h_content}")

    except Exception as e:
        return f"Error parsing articles: {str(e)}"

    return f"# {name}\n\n" + "\n".join(articles)

@mcp.tool()
def search_precedent(query: str) -> str:
    """
    Search for Korean legal precedents (판례) by query.
    Returns a list of matching precedents with their IDs and case numbers.
    """
    logger.info(f"Searching precedents for: {query}")
    # target='prec' for precedents
    data = client.search_law(query, target="prec")
    
    if 'PrecSearch' not in data or 'prec' not in data['PrecSearch']:
        return "No results found."
        
    precs = data['PrecSearch']['prec']
    if not isinstance(precs, list):
        precs = [precs]
    
    output = []
    for p in precs:
        name = p.get('사건명', 'Unknown')
        id = p.get('판례일련번호', 'Unknown')
        case_no = p.get('사건번호', 'Unknown')
        date = p.get('선고일자', 'Unknown')
        court = p.get('법원명', '')
        output.append(f"ID: {id} | Case: {case_no} | Name: {name} | Court: {court} | Date: {date}")
        
    return "\n".join(output)

@mcp.tool()
def get_precedent_detail(prec_id: str) -> str:
    """
    Get the full text/details of a specific precedent using its ID.
    Use 'search_precedent' first to find the ID.
    """
    logger.info(f"Getting precedent details for ID: {prec_id}")
    data = client.get_precedent_detail(prec_id)
    
    if 'PrecService' not in data:
        return "Error: Invalid response structure (Missing 'PrecService')"
        
    info = data['PrecService']
    
    # Extract key fields
    title = info.get('사건명', 'Unknown')
    case_no = info.get('사건번호', 'Unknown')
    date = info.get('선고일자', 'Unknown')
    court = info.get('법원명', 'Unknown')
    
    # HTML formatting is often used in content, might need stripping if we want pure text, 
    # but LLMs can handle basic HTML tags.
    summary = info.get('판결요지', '')
    content = info.get('판례내용', '')
    holding = info.get('판시사항', '')
    
    def clean_html(text):
        if not text: return ""
        text = text.replace("<br/>", "\n").replace("&lt;", "<").replace("&gt;", ">")
        return text
    
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

@mcp.tool()
def search_prec_const(query: str) -> str:
    """
    Search for Constitutional Court decisions (헌재결정례).
    Returns list with IDs and Case Numbers.
    """
    logger.info(f"Searching const. decisions for: {query}")
    data = client.search_law(query, target="detc")
    
    if 'DetcSearch' not in data or 'Detc' not in data['DetcSearch']:
        return "No results found."
        
    items = data['DetcSearch']['Detc']
    if not isinstance(items, list):
        items = [items]
        
    output = []
    for item in items:
        name = item.get('사건명', 'Unknown')
        id = item.get('헌재결정례일련번호', 'Unknown')
        case_no = item.get('사건번호', 'Unknown')
        date = item.get('종국일자', 'Unknown')
        output.append(f"ID: {id} | Case: {case_no} | Name: {name} | Date: {date}")
        
    return "\n".join(output)

@mcp.tool()
def get_prec_const_detail(detc_id: str) -> str:
    """
    Get details of a Constitutional Court decision.
    """
    logger.info(f"Getting const. decision details for ID: {detc_id}")
    data = client.get_prec_const_detail(detc_id)
    
    if 'DetcService' not in data:
        return "Error: Invalid response structure (Missing 'DetcService')"
        
    info = data['DetcService']
    
    title = info.get('사건명', 'Unknown')
    case_no = info.get('사건번호', 'Unknown')
    date = info.get('종국일자', 'Unknown')
    type_name = info.get('사건종류명', '')
    
    # Text fields
    holding = info.get('판시사항', '')
    summary = info.get('결정요지', '')
    content = info.get('전문', '')
    
    def clean_html(text):
        if not text: return ""
        text = str(text) # Ensure string
        text = text.replace("<br/>", "\n").replace("&lt;", "<").replace("&gt;", ">")
        # Remove CDATA if present (xmltodict usually handles this but just in case)
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

@mcp.tool()
def search_autonomous_law(query: str) -> str:
    """
    Search for Autonomous Laws (자치법규 - Ordinances/Rules of Local Gov).
    Returns list with IDs (MST) and Names.
    """
    logger.info(f"Searching autonomous laws for: {query}")
    data = client.search_law(query, target="ordin")
    
    if 'OrdinSearch' not in data or 'law' not in data['OrdinSearch']:
        return "No results found."
        
    items = data['OrdinSearch']['law']
    if not isinstance(items, list):
        items = [items]
        
    output = []
    for item in items:
        name = item.get('자치법규명', 'Unknown')
        # Important: Ordin uses '자치법규일련번호' which maps to MST param
        id = item.get('자치법규일련번호', 'Unknown')
        
        gov = item.get('지자체기관명', '')
        date = item.get('공포일자', '')
        type_name = item.get('자치법규종류', '') # e.g. 조례, 규칙
        
        output.append(f"ID: {id} | Gov: {gov} | Type: {type_name} | Name: {name} | Date: {date}")
        
    return "\n".join(output)

@mcp.tool()
def get_autonomous_law_detail(law_id: str) -> str:
    """
    Get details of an Autonomous Law.
    """
    logger.info(f"Getting autonomous law details for ID: {law_id}")
    data = client.get_autonomous_law_detail(law_id)
    
    # Root is 'LawService'?? Based on snippet.
    # But usually inside it is '자치법규기본정보'.
    if 'LawService' not in data:
        return "Error: Invalid response structure (Missing 'LawService')"
    
    root = data['LawService']
    info = root.get('자치법규기본정보', {})
    
    name = info.get('자치법규명', 'Unknown')
    gov = info.get('지자체기관명', '')
    
    # For content: Try to find '조문' (Articles) similar to Statutes
    # or '부칙' (Addenda)
    
    articles = []
    # In Ordin, articles might be under '조문' key in LawService or inside 기본정보?
    # Usually it's a sibling of 기본정보.
    
    jomun_section = root.get('조문', {})
    if jomun_section:
        # Check for '조문단위' (Standard Law) or '조' (Ordinance)
        body = jomun_section.get('조문단위') or jomun_section.get('조') or []
        
        if not isinstance(body, list):
            body = [body]
        
        for item in body:
            # Handle field name variations
            content = item.get('조문내용') or item.get('조내용') or ''
            content = content.strip()
            
            # Fallback for text-only nodes
            if not content and '#text' in item:
                 content = item['#text'].strip()
            
            no = item.get('조문번호', '?')
            title = item.get('조문제목') or item.get('조제목') or ''
            
            header = f"제{no}조({title})" if title else f"제{no}조"
            articles.append(f"{header}: {content}")
            
            # Simple handling of paragraphs for now
            if '항' in item:
                paragraphs = item['항']
                if not isinstance(paragraphs, list): paragraphs = [paragraphs]
                for p in paragraphs:
                    p_content = p.get('항내용', '').strip()
                    p_no = p.get('항번호', '')
                    if p_content: articles.append(f"  {p_no}. {p_content}")

    if not articles:
        articles.append("(No parsed articles found. The law might use a different structure or be empty.)")

    return f"# {name} ({gov})\n\n" + "\n".join(articles)

@mcp.tool()
def search_admin_rule(query: str) -> str:
    """
    Search for Administrative Rules (행정규칙 - Notices, Directives).
    Returns list with IDs and Names.
    """
    logger.info(f"Searching admin rules for: {query}")
    data = client.search_law(query, target="admrul")
    
    if 'AdmRulSearch' not in data or 'admrul' not in data['AdmRulSearch']:
        return "No results found."
        
    items = data['AdmRulSearch']['admrul']
    if not isinstance(items, list):
        items = [items]
        
    output = []
    for item in items:
        name = item.get('행정규칙명', 'Unknown')
        id = item.get('행정규칙일련번호', 'Unknown')
        dept = item.get('소관부처명', '')
        date = item.get('발령일자', '')
        type_name = item.get('행정규칙종류', '')
        
        output.append(f"ID: {id} | Dept: {dept} | Type: {type_name} | Name: {name} | Date: {date}")
        
    return "\n".join(output)

@mcp.tool()
def get_admin_rule_detail(adm_id: str) -> str:
    """
    Get details of an Administrative Rule.
    """
    logger.info(f"Getting admin rule details for ID: {adm_id}")
    data = client.get_admin_rule_detail(adm_id)
    
    if 'AdmRulService' not in data:
        return "Error: Invalid response structure (Missing 'AdmRulService')"
        
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

    # 1. '조문내용' (Article Content) usually contains the main text or articles
    if '조문내용' in root:
        content = root['조문내용']
        if isinstance(content, str):
             # Often it's just raw text or HTML-like text
             content_acc.append(clean_html(content))
        elif isinstance(content, list):
             # If it's a list, treat as lines?
             for c in content:
                 content_acc.append(clean_html(str(c)))
    
    # 2. Check for '전문' (Full text) if empty
    if not content_acc:
        full_text = root.get('전문', '')
        if full_text:
            content_acc.append(clean_html(full_text))
            
    if not content_acc:
        # Try '부칙' (Addenda) if main content empty?
        buchik = root.get('부칙')
        if buchik:
            content_acc.append("\n[부칙]\n" + clean_html(str(buchik)))
        else:
            content_acc.append("(No content found.)")
        
    return f"# {name} ({dept})\n\n" + "\n".join(content_acc)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
