from korean_law_mcp.main import search_korean_law, read_legal_resource
import logging

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO)

def test_search():
    print("=== Testing search_korean_law ===")
    
    # 1. Broad Search
    print("\n[Query: '학교폭력']")
    res = search_korean_law("학교폭력")
    print(res[:500] + "..." if len(res) > 500 else res)
    
    # 2. Smart Search (Article)
    print("\n[Query: '고등교육법 제20조']")
    res = search_korean_law("고등교육법 제20조")
    print(res[:500] + "..." if len(res) > 500 else res)

def test_read():
    print("\n=== Testing read_legal_resource ===")
    
    # 1. Read Statute (using ID from previous knowledge or search)
    # Let's try to read a known statute ID if possible, or just fail gracefully if ID is wrong
    # I'll use a dummy ID first to check error handling, then maybe parse from search?
    
    print("\n[Read: 'statute:invalid']")
    print(read_legal_resource("statute:invalid"))
    
    # Search first to get a valid ID
    search_res = search_korean_law("고등교육법")
    # Extract ID strictly for testing (Mocking the agent's behavior)
    import re
    match = re.search(r'ID: statute:(\d+)', search_res)
    if match:
        valid_id = match.group(1)
        print(f"\n[Read: 'statute:{valid_id}']")
        res = read_legal_resource(f"statute:{valid_id}")
        # Check if references are resolved (look for "Referenced Articles Resolution")
        print("Length:", len(res))
        if "Referenced Articles Resolution" in res:
            print("SUCCESS: Reference resolution triggered.")
        else:
            print("NOTE: No references resolved (might be none in text).")
            
        print("Snippet:", res[:200])
    else:
        print("Could not find statute ID to test read.")

if __name__ == "__main__":
    test_search()
    test_read()
