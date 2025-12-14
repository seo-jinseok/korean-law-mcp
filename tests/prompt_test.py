import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from korean_law_mcp.main import summarize_law, explain_legal_term, compare_laws

class TestPrompts(unittest.TestCase):
    def test_summarize_law(self):
        """Test summarize_law prompt"""
        print("\n>>> Testing prompt: summarize_law('265307')...")
        messages = summarize_law("265307") # Civil Act
        self.assertEqual(len(messages), 1)
        role = messages[0].role
        text = messages[0].content.text
        self.assertEqual(role, "user")
        self.assertIn("법령(ID: 265307)", text)
        self.assertIn("민법", text) # Check if actual law content is fetched
        print("[PASS] summarize_law")

    def test_explain_legal_term(self):
        """Test explain_legal_term prompt"""
        print("\n>>> Testing prompt: explain_legal_term('학교폭력')...")
        messages = explain_legal_term("학교폭력")
        self.assertEqual(len(messages), 1)
        text = messages[0].content.text
        self.assertIn("학교폭력", text)
        self.assertIn("검색 결과", text)
        print("[PASS] explain_legal_term")

    def test_compare_laws(self):
        """Test compare_laws prompt"""
        # Compare Art 103 vs Art 104 (using full law fetch as placeholder logic)
        # Note: In real usage, IDs should be valid. Using Civil Act twice for test speed/stability
        print("\n>>> Testing prompt: compare_laws('265307', '265307')...")
        messages = compare_laws("265307", "265307") 
        text = messages[0].content.text
        self.assertIn("법령 1 (ID: 265307)", text)
        self.assertIn("법령 2 (ID: 265307)", text)
        print("[PASS] compare_laws")

if __name__ == '__main__':
    unittest.main()
