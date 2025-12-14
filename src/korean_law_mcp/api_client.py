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

    def get_legal_term_list(self, query: str) -> Dict[str, Any]:
        """
        Search for legal terms (Law Terms).
        """
        # Endpoint: /DRF/lawSearch.do?target=lstrm&query={query}
        url = f"{self.BASE_URL}/DRF/lawSearch.do"
        params = {
            "OC": self.user_id,
            "target": "lstrm",
            "type": "XML",
            "query": query
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return xmltodict.parse(response.content)

    def get_legal_term_detail(self, term_id: str) -> Dict[str, Any]:
        """
        Get details of a legal term.
        """
        # Endpoint: /DRF/lawService.do?target=lstrm&MST={term_id} (or ID?)
        # Guide says ID or MST. Usually MST for terms.
        url = f"{self.BASE_URL}/DRF/lawService.do"
        params = {
            "OC": self.user_id,
            "target": "lstrm",
            "type": "XML",
            "MST": term_id # Verified in docs: Uses MST
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return xmltodict.parse(response.content)

    def get_statutory_interpretation_list(self, query: str) -> Dict[str, Any]:
        """
        Search for statutory interpretations (expc).
        """
        # Endpoint: /DRF/lawSearch.do?target=expc&query={query}
        url = f"{self.BASE_URL}/DRF/lawSearch.do"
        params = {
            "OC": self.user_id,
            "target": "expc",
            "type": "XML",
            "query": query
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return xmltodict.parse(response.content)

    def get_statutory_interpretation_detail(self, interp_id: str) -> Dict[str, Any]:
        """
        Get details of a statutory interpretation.
        """
        # Endpoint: /DRF/lawService.do?target=expc&ID={interp_id}
        url = f"{self.BASE_URL}/DRF/lawService.do"
        params = {
            "OC": self.user_id,
            "target": "expc",
            "type": "XML",
            "ID": interp_id # Verified in docs: Uses ID (sometimes MST, will try ID first)
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

        # Test Legal Term Search
        print("\nTesting get_legal_term_list('근로자')...")
        term_res = client.get_legal_term_list("근로자")
        if 'LawTermSearch' in term_res and 'lawTerm' in term_res['LawTermSearch']:
            items = term_res['LawTermSearch']['lawTerm']
            if not isinstance(items, list): items = [items]
            print(f"Found {len(items)} terms. First: {items[0].get('법령용어명')}")
        else:
            print("Term search failed/empty.")

        # Test Statutory Interpretation Search
        print("\nTesting get_statutory_interpretation_list('학교폭력')...")
        interp_res = client.get_statutory_interpretation_list("학교폭력")
        if 'Expc' in interp_res and 'expc' in interp_res['Expc']:
            items = interp_res['Expc']['expc']
            # items can be a single dict or list
            if not isinstance(items, list): items = [items]
            print(f"Found {len(items)} interpretations. First: {items[0].get('안건명')}")
        elif 'ExpcSearch' in interp_res:
             # Fallback just in case
            print("Found ExpcSearch (unexpected but handled)")
        else:
            print("Interpretation search failed/empty. Raw keys:", interp_res.keys())



    except Exception as e:
        print(f"Test failed: {e}")

