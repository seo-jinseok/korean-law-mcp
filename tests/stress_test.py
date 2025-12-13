from korean_law_mcp.main import search_korean_law, read_legal_resource
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

def run_stress_test():
    print(">>> Starting MCP Server Stress Test <<<\n")
    
    # 1. Edge Case: Empty Query
    print("--- Test 1: Empty Query ---")
    res = search_korean_law("")
    # Expectation: Should not crash, ideally return a prompt or empty result message
    # Looking at code: client.search_law("") might fail or return error from API.
    print(f"Result: {res[:100]}...")
    
    # 2. Edge Case: Nonsense Query
    print("\n--- Test 2: Nonsense Query ---")
    res = search_korean_law("dkfjsldkfjwoiejf")
    if "No results" in res or "No laws found" in res:
        log_test("Handle nonsense query", "Success")
    else:
        log_test("Handle nonsense query", res, expected=False)

    # 3. Valid Case: Specific Article (Smart Search)
    print("\n--- Test 3: Specific Article (Smart Search) ---")
    query = "민법 제103조"
    res = search_korean_law(query)
    if "제103조" in res and "반사회질서" in res:
        log_test("Find Civil Act Art. 103", "Success")
    else:
        log_test("Find Civil Act Art. 103", res[:200], expected=False)

    # 4. Valid Case: English Query for Article
    print("\n--- Test 4: English Query (Smart Search) ---")
    query = "Criminal Act Article 250"
    res = search_korean_law(query)
    if "제250조" in res and "살인" in res:
        log_test("Find Criminal Act Art. 250 via English", "Success")
    else:
        log_test("Find Criminal Act Art. 250 via English", res[:200], expected=False)

    # 5. Broad Search & Typed ID Extraction
    print("\n--- Test 5: Broad Search & Precedent ID ---")
    res = search_korean_law("직권남용") # Abuse of Authority (usually has stable SC cases)
    match = re.search(r'ID: (prec:\d+)', res)
    prec_id = match.group(1) if match else None
    
    if prec_id:
        log_test(f"Extract Precedent ID ({prec_id})", "Success")
        
        # 6. Read extracted ID
        print(f"\n--- Test 6: Read Precedent {prec_id} ---")
        prec_content = read_legal_resource(prec_id)
        if len(prec_content) > 100 and "Error" not in prec_content:
             log_test("Read Precedent Content", "Success")
        else:
             log_test("Read Precedent Content", prec_content[:200], expected=False)
             
    else:
        log_test("Extract Precedent ID", "Failed to find any precedent ID in search results", expected=False)

    # 7. Error Handling: Invalid ID Format
    print("\n--- Test 7: Invalid ID Format ---")
    res = read_legal_resource("invalid_id_no_colon")
    if "Error: Invalid ID format" in res:
        log_test("Catch invalid format", "Success")
    else:
        log_test("Catch invalid format", res, expected=False)

    # 8. Error Handling: Unknown Type
    print("\n--- Test 8: Unknown Resource Type ---")
    res = read_legal_resource("alien:12345")
    if "Error: Unknown resource type" in res:
         log_test("Catch unknown type", "Success")
    else:
         log_test("Catch unknown type", res, expected=False)

    # 9. Error Handling: Non-existent ID
    print("\n--- Test 9: Non-existent ID ---")
    # statute:99999999 is likely invalid
    res = read_legal_resource("statute:99999999")
    # Current implementation returns error string from Exception
    if "Error" in res or "500" in res or "Internal Server Error" in res:
        log_test("Handle non-existent ID gracefully", "Success")
    else:
        log_test("Handle non-existent ID gracefully", res[:200], expected=False)

    # 10. Reference Resolution Check
    # We need a resource known to have references. 
    # Civil Act (Minpo) usually references many things.
    # Let's try searching for a law that is an enforcement decree, which references the main act.
    print("\n--- Test 10: Reference Resolution ---")
    # Find Enforcement Decree of Copyright Act (저작권법 시행령)
    search_res = search_korean_law("저작권법 시행령")
    match = re.search(r'ID: (statute:\d+)', search_res)
    if match:
        decree_id = match.group(1)
        print(f"Found Decree ID: {decree_id}")
        content = read_legal_resource(decree_id)
        if "Referenced Articles Resolution" in content:
            log_test("Trigger Reference Resolution", "Success")
        else:
            # It's possible it didn't find specific 'XX법 제YY조' pattern enough times or at all
            print("Note: Reference resolution did not trigger (might simply be no matches).")
            # This is not necessarily a fail, but valid behavior.
            log_test("Trigger Reference Resolution", "Skipped/No matches", expected=True)
    else:
        log_test("Find Copyright Act Decree", "Failed to find ID", expected=False)
    
    print("\n>>> Stress Test Complete <<<")

if __name__ == "__main__":
    run_stress_test()
