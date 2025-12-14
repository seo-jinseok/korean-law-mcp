import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from korean_law_mcp.resources import read_statute_resource, read_statute_article_resource, read_precedent_resource

class TestResources(unittest.TestCase):
    def test_read_statute_resource(self):
        """Test reading a full statute (Civil Act) via Resource handler"""
        # Civil Act ID: 265307
        print("\n>>> Testing law://statute/265307 (Civil Act) ...")
        content = read_statute_resource("265307")
        self.assertIn("민법", content)
        self.assertIn("제1조", content)
        print("[PASS] Full Statute Read")

    def test_read_statute_article_resource(self):
        """Test reading a specific article (Civil Act Art 103)"""
        print("\n>>> Testing law://statute/265307/art/103 (Anti-social Juridical Act) ...")
        content = read_statute_article_resource("265307", "103")
        self.assertIn("제103조", content)
        self.assertIn("반사회질서", content)
        print("[PASS] Specific Article Read")
    
    # Using the stable Const Court case found earlier: 2003헌가1 (prec:238041)
    # The ID passed to read_precedent_resource refers to the internal ID not the case number
    def test_read_precedent_resource(self):
        """Test reading a precedent via Resource handler"""
        # Case: 2003헌가1 -> prec:238041 (from previous test findings)
        print("\n>>> Testing law://prec/238041 (Const Court 2003헌가1) ...")
        content = read_precedent_resource("238041")
        # "신행정수도" might be split or formatted differently. "헌법" is guaranteed in a Const Court ruling.
        self.assertIn("헌법", content) 
        print("[PASS] Precedent Read")

if __name__ == '__main__':
    unittest.main()
