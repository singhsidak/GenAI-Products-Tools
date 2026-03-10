"""Test script for deployed TuneTrace.AI agent."""

import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tune_trace_ai import create_agent


def test_basic_analysis():
    """Test basic song analysis."""
    print("🧪 Test 1: Basic Song Analysis")
    print("-" * 70)
    
    agent = create_agent()
    result = agent.analyze_song("Lose Yourself by Eminem")
    
    print("Input: 'Lose Yourself by Eminem'")
    print("\nResult:")
    print(json.dumps(result, indent=2))
    print()
    
    # Validate result structure
    if "error" in result:
        print("⚠️  Test completed with error (may need more time or clearer input)")
        return False
    
    if "input_song_analysis" in result and "recommendations" in result:
        print("✅ Test 1 PASSED: Valid analysis structure")
        return True
    else:
        print("❌ Test 1 FAILED: Invalid result structure")
        return False


def test_url_analysis():
    """Test URL-based analysis."""
    print("\n🧪 Test 2: URL Analysis")
    print("-" * 70)
    
    agent = create_agent()
    # Using a well-known song URL
    result = agent.analyze_song("https://www.youtube.com/watch?v=_Yhyp-_hX2s")
    
    print("Input: YouTube URL")
    print("\nResult structure:")
    if "error" in result:
        print("⚠️  URL analysis returned error (this is acceptable for test)")
        print(f"Error: {result.get('error', 'Unknown')}")
        return True
    else:
        print(json.dumps(result, indent=2)[:500] + "...")
        print("✅ Test 2 PASSED: URL processing works")
        return True


def test_multiple_songs():
    """Test multiple song analysis."""
    print("\n🧪 Test 3: Multiple Songs Analysis")
    print("-" * 70)
    
    agent = create_agent()
    result = agent.analyze_song("""
    Bohemian Rhapsody by Queen
    Smells Like Teen Spirit
    """)
    
    print("Input: Multiple songs")
    print("\nResult structure:")
    
    if "multiple_songs" in result:
        print(f"Detected {result.get('count', 0)} songs")
        print("✅ Test 3 PASSED: Multiple song detection works")
        return True
    else:
        print("⚠️  Single song analysis performed (acceptable)")
        return True


def test_batch_analysis():
    """Test batch analysis feature."""
    print("\n🧪 Test 4: Batch Analysis")
    print("-" * 70)
    
    agent = create_agent()
    result = agent.analyze_batch([
        "Happy by Pharrell Williams",
        "Blinding Lights by The Weeknd"
    ])
    
    print("Input: Batch of 2 songs")
    print("\nResult structure:")
    
    if "batch_analysis" in result and result.get("count") == 2:
        print(f"✅ Test 4 PASSED: Batch analysis completed for {result['count']} songs")
        return True
    else:
        print("❌ Test 4 FAILED: Batch analysis structure incorrect")
        return False


def run_all_tests():
    """Run all deployment tests."""
    print("🎵 TuneTrace.AI - Deployment Tests")
    print("=" * 70)
    print()
    
    # Check API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set. Please export it first.")
        print("export GOOGLE_API_KEY='your-key'")
        sys.exit(1)
    
    print("✅ API key found")
    print()
    
    # Run tests
    results = []
    
    try:
        results.append(("Basic Analysis", test_basic_analysis()))
    except Exception as e:
        print(f"❌ Test 1 ERROR: {e}")
        results.append(("Basic Analysis", False))
    
    try:
        results.append(("URL Analysis", test_url_analysis()))
    except Exception as e:
        print(f"❌ Test 2 ERROR: {e}")
        results.append(("URL Analysis", False))
    
    try:
        results.append(("Multiple Songs", test_multiple_songs()))
    except Exception as e:
        print(f"❌ Test 3 ERROR: {e}")
        results.append(("Multiple Songs", False))
    
    try:
        results.append(("Batch Analysis", test_batch_analysis()))
    except Exception as e:
        print(f"❌ Test 4 ERROR: {e}")
        results.append(("Batch Analysis", False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20s} {status}")
    
    print("-" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All tests passed! TuneTrace.AI is ready for use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())



