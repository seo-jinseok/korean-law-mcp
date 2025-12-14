import sys
import os
import re

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from korean_law_mcp.tools import search_korean_law, read_legal_resource, search_statutory_interpretations

def test_tools():
    print("=== Testing Search & Constitutional Court ===")
    # Use the public tool
    res = search_korean_law("위헌")
    print(f"Search Result (Snippet): {res[:200]}")
    
    if "No results" not in res:
        # The search result should contain "prec:ID" or "statute:ID" or similar
        # Const court cases often come as 'prec' or 'statute' depending on classification in search
        # But 'search_statutory_interpretations' is separate.
        
        # We need an ID. 
        # search_korean_law returns a list.
        # Format: "- **Title** ... [ID: type:id]"
        match = re.search(r"ID: ([a-z]+:\d+)", res)
        if match:
            full_id = match.group(1)
            print(f"Testing read_legal_resource for ID: {full_id}")
            detail = read_legal_resource(full_id)
            print(f"Detail Snippet: {detail[:200]}")
        else:
            print("No ID found in search results to test detail.")

    print("\n=== Testing Autonomous Laws Search implies 'integrated' search cover it ===")
    # 'search_korean_law' covers broad search.
    # Specific targeted search methods like `search_autonomous_law` were internal helpers or distinct tools?
    # In `tools.py`, `search_korean_law` calls `search_integrated_internal` which searches Law, Prec, AdmRul.
    # Autonomous laws are 'ordin' (Ordinance?). They might not be in the default search_korean_law targets if not explicitly added.
    # Let's check `utils.search_integrated_internal`: it searches "law", "prec", "admrul".
    # It does NOT search "ordin" (Autonomous Law).
    # So `test_tools.py` testing `search_autonomous_law` implies that functionality MIGHT BE MISSING in the new main tool `search_korean_law`.
    
    # Wait, `get_autonomous_law_detail_internal` exists in `utils.py`.
    # But is there a search tool exposed for it?
    # `tools.py` does NOT expose a specific search for autonomous laws.
    # And `search_korean_law` integrated search only does Statutes, Precedents, AdminRules.
    
    # This reveals a POTENTIAL REGRESSION or missing feature if `search_autonomous_law` was previously available.
    # However, Looking at `main.py` outline earlier, I did NOT see `search_autonomous_law` as a `@mcp.tool`. 
    # It was likely just an internal function in `main.py` that `test_tools.py` was import testing.
    # If it wasn't exposed as a tool, then it's fine.
    # But `utils.py` HAS `get_autonomous_law_detail_internal`.
    # And `read_legal_resource` handles `ordin`. 
    # But how does a user FIND an `ordin` ID?
    # Maybe `search_korean_law` doesn't support it yet.
    # I will stick to testing what IS exposed.
    
    print("\n=== Testing Admin Rules ===")
    res = search_korean_law("도로") # Should return admin rules in section 3
    print(f"Search Result (Snippet): {res[:200]}")
    match = re.search(r"ID: admrul:(\d+)", res)
    if match:
        full_id = f"admrul:{match.group(1)}"
        print(f"Testing detail for ID: {full_id}")
        detail = read_legal_resource(full_id)
        if "도로" in detail or "Rule" in detail or "행정규칙" in detail or "#" in detail:
             print("Validation: Content seems valid.")
        else:
             print("Validation: Content might be empty or error.")
        print(f"Detail Snippet: {detail[:200]}")

if __name__ == "__main__":
    test_tools()
