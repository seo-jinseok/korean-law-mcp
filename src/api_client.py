import os
import requests
import xmltodict
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class KoreanLawClient:
    BASE_URL = "https://www.law.go.kr"
    
    def __init__(self):
        self.user_id = os.getenv("OPEN_LAW_ID")
        if not self.user_id:
            raise ValueError("OPEN_LAW_ID environment variable is not set")

    def search_law(self, query: str, target: str = "law") -> Dict[str, Any]:
        """
        Search for laws/regulations.
        Target: 'law' (statute), 'prec' (precedent), etc.
        """
        # Endpoint construction (this is a guess based on standard patterns, verifying with actual docs is key)
        # Usually: /DRF/lawSearch.do?OC={user_id}&target={target}&type=XML&query={query}
        url = f"{self.BASE_URL}/DRF/lawSearch.do"
        params = {
            "OC": self.user_id,
            "target": target,
            "type": "XML",
            "query": query
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Parse XML to Dict
        data = xmltodict.parse(response.content)
        return data

    def get_law_detail(self, law_id: str) -> Dict[str, Any]:
        """
        Get details of a specific law (statute).
        """
        # Endpoint: /DRF/lawService.do?OC={user_id}&target=law&type=XML&MST={law_id}
        url = f"{self.BASE_URL}/DRF/lawService.do"
        params = {
            "OC": self.user_id,
            "target": "law",
            "type": "XML",
            "MST": law_id
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = xmltodict.parse(response.content)
        return data

    def get_precedent_detail(self, prec_id: str) -> Dict[str, Any]:
        """
        Get details of a specific precedent.
        """
        # Endpoint: /DRF/lawService.do?OC={user_id}&target=prec&type=XML&ID={prec_id}
        url = f"{self.BASE_URL}/DRF/lawService.do"
        params = {
            "OC": self.user_id,
            "target": "prec",
            "type": "XML",
            "ID": prec_id
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = xmltodict.parse(response.content)
        return data

    def get_admin_rule_detail(self, adm_id: str) -> Dict[str, Any]:
        """
        Get details of an administrative rule (admrul).
        """
        # Endpoint: /DRF/lawService.do?target=admrul&ID={adm_id}
        url = f"{self.BASE_URL}/DRF/lawService.do"
        params = {
            "OC": self.user_id,
            "target": "admrul",
            "type": "XML",
            "ID": adm_id
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return xmltodict.parse(response.content)

    def get_prec_const_detail(self, detc_id: str) -> Dict[str, Any]:
        """
        Get details of a Constitutional Court decision (detc).
        """
        # Endpoint: /DRF/lawService.do?target=detc&ID={detc_id}
        url = f"{self.BASE_URL}/DRF/lawService.do"
        params = {
            "OC": self.user_id,
            "target": "detc",
            "type": "XML",
            "ID": detc_id
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return xmltodict.parse(response.content)

    def get_autonomous_law_detail(self, ordin_id: str) -> Dict[str, Any]:
        """
        Get details of an autonomous law (ordin).
        Note: Uses 'MST' parameter instead of 'ID'.
        """
        # Endpoint: /DRF/lawService.do?target=ordin&MST={ordin_id}
        url = f"{self.BASE_URL}/DRF/lawService.do"
        params = {
            "OC": self.user_id,
            "target": "ordin",
            "type": "XML",
            "MST": ordin_id
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return xmltodict.parse(response.content)

if __name__ == "__main__":
    # Test connection
    try:
        client = KoreanLawClient()
        print(f"Client initialized with ID: {client.user_id}")
        
        # Try a simple search for "건축법" (Building Act)
        print("Testing search_law('건축법')...")
        result = client.search_law("건축법")
        print("Search successful!")
        # Print a snippet of the result to verify structure
        if 'LawSearch' in result and 'law' in result['LawSearch']:
            laws = result['LawSearch']['law']
            if isinstance(laws, list):
                print(f"Found {len(laws)} laws. First one: {laws[0].get('법령명한글')}")
            else:
                print(f"Found 1 law: {laws.get('법령명한글')}")
        else:
            print("Response structure unexpected:", result.keys())
            
    except Exception as e:
        print(f"Test failed: {e}")
