import sys
import os
import requests
import xmltodict
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
load_dotenv()

USER_ID = os.getenv("OPEN_LAW_ID")
BASE_URL = "https://www.law.go.kr"

def inspect_prec_relationships():
    prec_info = "238041" # Const Court case known to work
    print(f"Target Precedent ID: {prec_info}")
    print(f"Target Precedent ID: {prec_info}")
    
    print(f"\n>>> Inspecting Precedent ID: {prec_info} ...")
    # Precedent detail uses ID parameter
    detail_url = f"{BASE_URL}/DRF/lawService.do?OC={USER_ID}&target=prec&ID={prec_info}&type=XML"
    resp_detail = requests.get(detail_url)
    
    print("\n[Raw Check] '참조' in text?", "참조" in resp_detail.text)
    print("\n[Raw Check] '판례' in text?", "판례" in resp_detail.text)

    d_data = xmltodict.parse(resp_detail.text)
    print("\n[Raw Parsing] Top Keys:", d_data.keys())
    
    # Try to find meaningful root
    root_key = list(d_data.keys())[0]
    root = d_data[root_key]
    
    print(f"Root Key: {root_key}")
    print("Root Keys:", root.keys())
    
    # Print finding referenced stuff
    if '참조조문' in root:
        print(f"Found Referenced Articles: {root['참조조문']}")
    elif '참조조문' in str(root):
         print("Found '참조조문' in values somewhere.")
         
    # Print snippet
    print("\nSnippet:\n", resp_detail.text[:1000])

def inspect_relationships(law_id):
    print(f"\n>>> Inspecting Law ID: {law_id} for relationships...")
    # Target 'law' uses MST parameter for ID usually
    url = f"{BASE_URL}/DRF/lawService.do?OC={USER_ID}&target=law&MST={law_id}&type=XML"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching")
        return

    print("\n[Raw Check] '참조' in text?", "참조" in response.text)
    print("\n[Raw Check] '판례' in text?", "판례" in response.text)
    
    # Dump first few lines if needed
    # print(response.text[:1000])

    data = xmltodict.parse(response.text)
    # law_data might be None if 'Law' key is missing
    # For Korean API, root often is '법령'
    law_data = data.get('Law') or data.get('법령')
    if not law_data:
        print("No 'Law' or '법령' key found. Top keys:", data.keys())
        return

    print("Law Data Type:", type(law_data))
    if isinstance(law_data, str):
        print("Law Data is string:", law_data[:200])
        return

    # Check for likely relationship fields
    keys = law_data.keys()
    print("Top level keys:", keys)
    
    # Check Basic Info
    print("\n[Basic Info] Keys:", law_data.get('기본정보', {}).keys())

    # Check inside articles for references
    jomun_section = law_data.get('조문', {})
    jomun = jomun_section.get('조문단위', [])
    if not isinstance(jomun, list):
        jomun = [jomun]
        
    found_ref = False
    print(f"\nScanning {len(jomun)} articles for references...")
    
    for art in jomun:
        keys = art.keys()
        # semantic check
        if '참조조문' in keys:
            print(f"\n[Found Relations] Article {art.get('조문번호')}:")
            print(f"  Referenced: {art['참조조문']}")
            found_ref = True
        
        if '판례광장' in keys or '관련판례' in keys:
             print(f"\n[Found Relations] Article {art.get('조문번호')} (Cases):")
             print(art) # print whole thing to see key name
             found_ref = True
             
    if not found_ref:
        print("No '참조조문' or related keys found in any article.")

if __name__ == "__main__":
    if not USER_ID:
        print("OPEN_LAW_ID not set")
        sys.exit(1)
    inspect_prec_relationships()
    # Civil Act (265307) likely has limits of references
    inspect_relationships("265307")
