from src.main import search_prec_const, get_prec_const_detail, search_autonomous_law, get_autonomous_law_detail, search_admin_rule, get_admin_rule_detail

def test_tools():
    print("=== Testing Constitutional Court ===")
    res = search_prec_const("위헌")
    print(f"Search Result (Snippet): {res[:200]}")
    if "No results" not in res:
        # Extract an ID to test detail
        import re
        match = re.search(r"ID: (\d+)", res)
        if match:
            id = match.group(1)
            print(f"Testing detail for ID: {id}")
            detail = get_prec_const_detail(id)
            print(f"Detail Snippet: {detail[:200]}")

    print("\n=== Testing Autonomous Laws ===")
    res = search_autonomous_law("도로")
    print(f"Search Result (Snippet): {res[:200]}")
    if "No results" not in res:
        match = re.search(r"ID: (\d+)", res)
        if match:
            id = match.group(1)
            print(f"Testing detail for ID: {id}")
            detail = get_autonomous_law_detail(id)
            print(f"Detail Snippet: {detail[:200]}")

    print("\n=== Testing Admin Rules ===")
    res = search_admin_rule("도로")
    print(f"Search Result (Snippet): {res[:200]}")
    if "No results" not in res:
        match = re.search(r"ID: (\d+)", res)
        if match:
            id = match.group(1)
            print(f"Testing detail for ID: {id}")
            detail = get_admin_rule_detail(id)
            print(f"Detail Snippet: {detail[:200]}")

if __name__ == "__main__":
    test_tools()
