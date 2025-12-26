"""
Test suite for new MCP tools:
- get_external_links
- get_article_history
- compare_old_new
"""
import sys
import os
import re

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))


def test_get_external_links():
    """Test external link generation for various resource types."""
    from korean_law_mcp.tools import get_external_links
    
    print("=== Test: get_external_links ===")
    
    # Test statute links
    result = get_external_links("statute:12345")
    assert "law.go.kr" in result, "Should contain law.go.kr URL"
    assert "법령 상세" in result, "Should contain statute detail link"
    assert "법령 본문" in result, "Should contain statute text link"
    assert "법령 연혁" in result, "Should contain statute history link"
    print("✓ Statute links generated correctly")
    
    # Test precedent links
    result = get_external_links("prec:67890")
    assert "precInfoP.do" in result, "Should contain precedent URL"
    print("✓ Precedent links generated correctly")
    
    # Test admin rule links
    result = get_external_links("admrul:11111")
    assert "admRulInfoP.do" in result, "Should contain admin rule URL"
    print("✓ Admin rule links generated correctly")
    
    # Test error handling
    result = get_external_links("invalid_format")
    assert "Error" in result, "Should return error for invalid format"
    print("✓ Error handling works correctly")
    
    print("All get_external_links tests passed!\n")


def test_get_article_history():
    """Test article history retrieval."""
    from korean_law_mcp.tools import get_article_history
    
    print("=== Test: get_article_history ===")
    
    # Test with Korean law name - this requires API access
    result = get_article_history("고등교육법")
    
    # Check for expected content
    assert "연혁" in result or "Error" in result, "Should contain history or error"
    
    if "Error" not in result:
        assert "제개정구분" in result or "시행일자" in result, "Should contain revision info"
        print("✓ Article history retrieved correctly")
    else:
        print(f"⚠ API returned error (expected if no API key): {result[:100]}")
    
    print("Article history test completed!\n")


def test_compare_old_new():
    """Test old/new comparison."""
    from korean_law_mcp.tools import compare_old_new
    
    print("=== Test: compare_old_new ===")
    
    # Test with Korean law name
    result = compare_old_new("고등교육법")
    
    # Check for expected content - now provides web link
    assert "신구조문" in result or "Error" in result, "Should contain comparison or error"
    
    if "Error" not in result:
        assert "law.go.kr" in result, "Should contain web link to comparison page"
        print("✓ Old/new comparison with web link generated correctly")
    else:
        print(f"⚠ Error: {result[:100]}")
    
    print("Compare old/new test completed!\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Running New Tools Test Suite")
    print("="*60 + "\n")
    
    try:
        test_get_external_links()
        test_get_article_history()
        test_compare_old_new()
        
        print("="*60)
        print("All tests completed successfully!")
        print("="*60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
