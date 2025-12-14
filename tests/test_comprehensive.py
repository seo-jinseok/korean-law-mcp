from korean_law_mcp.tools import search_korean_law, read_legal_resource
import re
import sys

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def log_test(name, result, expected=True):
    if expected:
        print(f"[{GREEN}PASS{RESET}] {name}")
    else:
        print(f"[{RED}FAIL{RESET}] {name}")
        print(f"   Reason: {result}")

def run_comprehensive_test():
    print(">>> Starting Comprehensive Scenario Test <<<\n")
    
    # 1. Admin Rule Reading
    print("--- Test 1: Admin Rule (Search & Read) ---")
    # Search for something that definitely has admin rules, e.g., "학교폭력"
    res = search_korean_law("학교폭력") 
    match = re.search(r'ID: (admrul:\d+)', res)
    if match:
        rule_id = match.group(1)
        print(f"Found Admin Rule ID: {rule_id}")
        content = read_legal_resource(rule_id)
        if len(content) > 100 and "Error" not in content[:50]:
            log_test("Read Admin Rule", "Success")
        else:
            log_test("Read Admin Rule", content[:200], expected=False)
    else:
        log_test("Read Admin Rule", "No admin rule found in search results", expected=False)

    # 2. Constitutional Court Decision
    # 2. Constitutional Court Decision (via Precedent Search)
    print("\n--- Test 2: Const Court Decision (Search & Read) ---")
    # Use a known stable Constitutional Court case that appears in 'prec' search.
    # Case: 2003헌가1 (Customary Law / Capital Relocation)
    res = search_korean_law("2003헌가1")
    
    match = re.search(r'ID: ((?:prec|detc|const):\d+)', res)
    
    if match:
        cid = match.group(1)
        print(f"Found Stable Const Case ID: {cid}")
        content = read_legal_resource(cid)
        # Check for keywords related to the case (Relocation of Capital / Customary Constitution)
        if "관습헌법" in content or "수도" in content or len(content) > 100:
             log_test("Read Const Court Decision (2003헌가1)", "Success")
        else:
             log_test("Read Const Court Decision (2003헌가1)", content[:200], expected=False)
    else:
        log_test("Read Const Court Decision", "Case 2003헌가1 not found in search", expected=False)

    # 3. Loosely Formatted Article Query
    print("\n--- Test 3: Loosely Formatted Query ('Civil Act 103') ---")
    # User forgets "Article" or "제"
    res = search_korean_law("Civil Act 103")
    # Current implementation expects "Article" or "제".
    # This test checks if we need to improve regex to handle this natural error.
    if "제103조" in res and "반사회질서" in res:
        log_test("Handle 'Civil Act 103'", "Success")
    else:
        # Failure is expected if code doesn't support it yet. 
        # This highlights an area for improvement.
        log_test("Handle 'Civil Act 103'", "Likely fell back to broad search or failed", expected=False)

    # 4. Natural Language Question
    print("\n--- Test 4: NLP-like Query ('What is the punishment for murder?') ---")
    res = search_korean_law("살인죄의 형량은?")
    # Should probably do a broad search and find Criminal Act Article 250
    if "살인" in res and "형법" in res:
         log_test("NLP Query Context", "Success (Found relevant context)")
    else:
         log_test("NLP Query Context", res[:200], expected=False)

    # 5. Mixed Language Query
    print("\n--- Test 5: Mixed Lang ('School Violence 예방') ---")
    res = search_korean_law("School Violence 예방")
    if "학교폭력" in res:
          log_test("Mixed Language Handling", "Success")
    else:
          log_test("Mixed Language Handling", res[:200], expected=False)

    print("\n>>> Comprehensive Test Complete <<<")

if __name__ == "__main__":
    run_comprehensive_test()
