import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from korean_law_mcp.tools import explore_legal_chain
from korean_law_mcp.utils import resolve_references, resolve_delegation

def test_deep_search():
    print("--- Testing Deep Search (Higher Education Act Art 20) ---")
    query = "고등교육법 제20조"
    result = explore_legal_chain(query)
    
    print(f"Result Length: {len(result)}")
    print(result[:1500]) # First 1500 chars

    if "**학교(School)**" in result or "학년도" in result or "조직" in result: 
        print("\n✅ Main Text Found")
    
    if "대통령령" in result and "Enforcement Decree" in result or "시행령" in result:
         print("\n✅ Delegation Resolution Triggered")
    
    # Check for linked decree content
    # Art 20 deals with "School Organization", usually delegates to Decree.
    # Decree should mention "법 제20조"
    if "법 제20조" in result:
        print("\n✅ Back-reference in Decree Found")

if __name__ == "__main__":
    test_deep_search()
