from src.api_client import KoreanLawClient
import requests
import xmltodict

def test_new_targets():
    client = KoreanLawClient()
    
    # Candidate codes to test. 
    # Based on Law.go.kr patterns:
    # Admin Rules: admr
    # Abstract/Const. Court: detc ?
    # Autonomous: ordin ? 
    
    # Exhaustive list for Administrative Rules
    targets_to_test = [
        ("detc", "Constitutional Court"), 
        ("ordin", "Autonomous Laws"),
        ("admr", "Admin Rules (Lower case)"),
        ("Admr", "Admin Rules (Title case)"),
        ("admRul", "Admin Rules (Camel)"),
        ("admrul", "Admin Rules (admrul)"),
        ("admin", "Admin Rules (admin)"),
    ]
    
    query = "도로"
    
    for code, desc in targets_to_test:
        print(f"\n--- Testing {desc} [Target: {code}] ---")
        try:
            url = f"{client.BASE_URL}/DRF/lawSearch.do"
            params = {
                "OC": client.user_id,
                "target": code,
                "type": "XML",
                "query": query
            }
            # Manually call to inspect raw response
            resp = requests.get(url, params=params)
            print(f"Status Code: {resp.status_code}")
            if len(resp.content) < 500:
                print(f"Raw Response: {resp.text}")
            
            if resp.status_code == 200:
                try:
                    res = xmltodict.parse(resp.content)
                    root_func = lambda d: next(iter(d))
                    root = root_func(res)
                    print(f"Parsed Root: {root}")
                    
                    # Logic to find items
                    if root:
                        # Find list key
                        keys = list(res[root].keys())
                        # Exclude metadata
                        list_key = next((k for k in keys if k not in ['target', '키워드', 'section', 'totalCnt', 'page', 'numOfRows', 'resultCode', 'resultMsg']), None)
                        if list_key:
                            print(f"Found List Key: {list_key}")
                            items = res[root][list_key]
                            if not isinstance(items, list):
                                items = [items]
                            
                            if items:
                                item = items[0]
                                print(f"First Item Keys: {item.keys()}")
                                
                                # Detail Fetch Challenge
                                # Ordin -> Likely MST
                                # Detc -> Likely ID
                                # Admr -> ??
                                
                                id_fields = [k for k in item.keys() if '일련번호' in k]
                                if id_fields:
                                    my_id = item[id_fields[0]]
                                    print(f"Fetch ID: {my_id}")
                                    
                                    # Request Detail
                                    d_url = f"{client.BASE_URL}/DRF/lawService.do"
                                    # Logic: If code is 'ordin', use MST? If 'detc', use ID?
                                    
                                    d_params = {
                                        "OC": client.user_id,
                                        "target": code,
                                        "type": "XML"
                                    }
                                    
                                    if code == 'ordin':
                                        d_params['MST'] = my_id
                                    else:
                                        d_params['ID'] = my_id
                                        
                                    
                                    d_resp = requests.get(d_url, params=d_params)
                                    print(f"Detail Status: {d_resp.status_code}")
                                    if d_resp.status_code == 200:
                                        try:
                                            d_data = xmltodict.parse(d_resp.content)
                                            root_key = list(d_data.keys())[0]
                                            print(f"Detail Root Key: {root_key}")
                                            print(f"Inner Keys: {d_data[root_key].keys()}")
                                            # Check for potential content fields
                                            print(f"Found Content Fields: {found}")
                                            
                                            if '조문' in d_data[root_key]:
                                                jomun = d_data[root_key]['조문']
                                                print(f"Jomun Type: {type(jomun)}")
                                                if isinstance(jomun, dict):
                                                    print(f"Jomun Keys: {jomun.keys()}")
                                                # Check commonly used '조문단위'
                                                if isinstance(jomun, dict) and '조문단위' in jomun:
                                                    units = jomun['조문단위']
                                                    if isinstance(units, list):
                                                        print(f"Jomun Units Count: {len(units)}")
                                                        print(f"First Unit keys: {units[0].keys()}")
                                                    else:
                                                        print(f"Jomun Unit keys: {units.keys()}")
                                                        
                                            if '조문내용' in d_data[root_key]:
                                                content = d_data[root_key]['조문내용']
                                                print(f"JomunContent Type: {type(content)}")
                                                if isinstance(content, str):
                                                    print(f"Content Start: {content[:100]}")
                                                elif isinstance(content, dict):
                                                    print(f"Content Keys: {content.keys()}")
                                                elif isinstance(content, list):
                                                    print(f"Content List Len: {len(content)}")
                                                    print(f"First Content Item: {content[0]}")
                                        except Exception as e:
                                            print(f"Parse Debug Error: {e}")
                                            print(f"Raw Snippet (500 chars): {d_resp.text[:500]}")
                                    
                except Exception as xml_e:
                    print(f"XML Parse Error: {xml_e}")
                    
        except Exception as e:
            print(f"General Error: {e}")

if __name__ == "__main__":
    test_new_targets()
