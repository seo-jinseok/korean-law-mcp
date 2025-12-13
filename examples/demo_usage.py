import re
import sys
import os

# Add src to sys.path to allow importing the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from korean_law_mcp.main import search_korean_law, read_legal_resource

def run_demo():
    print("=== 🇰🇷 Korean Law MCP Agentic Demo ===")
    print("Scenario: User asks 'What is the definition of School Violence and show me a related case.'\n")

    # Step 1: Find Definition (Smart Statute Search)
    print("🤖 Agent Action: Searching for '학교폭력예방 및 대책에 관한 법률 제2조' (Definition)...")
    definition_result = search_korean_law("학교폭력예방 및 대책에 관한 법률 제2조")
    print("\n📄 [Result - Definition]:")
    print(definition_result)
    print("-" * 60)

    # Step 2: Search for Precedents (Integrated Search)
    print("\n🤖 Agent Action: Searching for '학교폭력' (Broad Search)...")
    search_result = search_korean_law("학교폭력")
    print("\n🔍 [Result - Search Summary]:")
    print(search_result)
    
    # Step 3: Extract a Precedent ID and Read it
    # Regex to find a precedent ID: "ID: prec:(\d+)"
    match = re.search(r'ID: (prec:\d+)', search_result)
    if match:
        prec_id = match.group(1)
        print(f"\n🤖 Agent Action: Found Precedent ID '{prec_id}'. Reading full content...")
        
        content = read_legal_resource(prec_id)
        
        print("\n📜 [Result - Full Precedent Content (Snippet)]:")
        print(content[:1000] + "\n... (truncated) ...") # Print first 1000 chars
        
    else:
        print("\n⚠️ No precedent ID found in search results.")

    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    run_demo()
