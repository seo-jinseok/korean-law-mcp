import mcp.types as types
from .server import mcp
from .utils import get_statute_detail_internal
# Import the tool function to reuse its logic
from .tools import search_korean_law

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
