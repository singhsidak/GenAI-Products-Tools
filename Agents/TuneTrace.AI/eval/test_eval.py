"""Evaluation script for TuneTrace.AI agent."""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tune_trace_ai import create_agent


def load_test_data():
    """Load test songs data."""
    data_path = Path(__file__).parent / "data" / "test_songs.json"
    with open(data_path, "r") as f:
        return json.load(f)


def evaluate_single_song(agent, test_case):
    """Evaluate a single song analysis."""
    print(f"\n📝 Testing: {test_case['input']}")
    print(f"Description: {test_case['description']}")
    print("-" * 70)
    
    try:
        result = agent.analyze_song(test_case['input'])
        
        # Check for errors
        if "error" in result:
            print(f"❌ Analysis failed: {result['error']}")
            return {
                "passed": False,
                "error": result['error'],
                "test_case": test_case['input']
            }
        
        # Check structure
        if "input_song_analysis" not in result:
            print("❌ Missing input_song_analysis")
            return {
                "passed": False,
                "error": "Missing input_song_analysis",
                "test_case": test_case['input']
            }
        
        # Extract analysis
        analysis = result.get("input_song_analysis", {})
        parameters = analysis.get("parameters", {})
        recommendations = result.get("recommendations", [])
        
        # Validate genre
        genre_data = parameters.get("Genre / Subgenre", {})
        if genre_data:
            genre_value = genre_data.get("value", {})
            if isinstance(genre_value, dict):
                detected_genre = genre_value.get("genre", "")
            else:
                detected_genre = str(genre_value)
            
            expected = test_case.get("expected_genre", "")
            genre_match = expected.lower() in detected_genre.lower()
            print(f"Genre: {detected_genre} {'✅' if genre_match else '⚠️'}")
        
        # Validate era
        era_data = parameters.get("Era / Decade", {})
        if era_data:
            detected_era = era_data.get("value", "")
            expected_era = test_case.get("expected_era", "")
            era_match = expected_era.lower() in detected_era.lower()
            print(f"Era: {detected_era} {'✅' if era_match else '⚠️'}")
        
        # Check recommendations
        print(f"\nRecommendations: {len(recommendations)}")
        if len(recommendations) == 3:
            for i, rec in enumerate(recommendations, 1):
                is_wildcard = "[WILDCARD]" in rec.get("rationale", "")
                wildcard_marker = " 🎲" if is_wildcard else ""
                print(f"  {i}. {rec.get('song_name')} by {rec.get('artist')}{wildcard_marker}")
            print("✅ All 3 recommendations provided")
        else:
            print(f"⚠️  Expected 3 recommendations, got {len(recommendations)}")
        
        # Check for wildcard
        wildcard_found = any("[WILDCARD]" in rec.get("rationale", "") for rec in recommendations)
        if wildcard_found:
            print("✅ Wildcard recommendation found")
        else:
            print("⚠️  No wildcard recommendation detected")
        
        # Success
        print("✅ Analysis completed successfully")
        return {
            "passed": True,
            "result": result,
            "test_case": test_case['input']
        }
        
    except Exception as e:
        print(f"❌ Exception during analysis: {e}")
        return {
            "passed": False,
            "error": str(e),
            "test_case": test_case['input']
        }


def run_evaluation():
    """Run full evaluation suite."""
    print("🎵 TuneTrace.AI - Evaluation Suite")
    print("=" * 70)
    
    # Check API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set")
        print("Please export it: export GOOGLE_API_KEY='your-key'")
        sys.exit(1)
    
    print("✅ API key found")
    
    # Load test data
    try:
        test_cases = load_test_data()
        print(f"✅ Loaded {len(test_cases)} test cases")
    except Exception as e:
        print(f"❌ Error loading test data: {e}")
        sys.exit(1)
    
    # Create agent
    try:
        agent = create_agent()
        print("✅ Agent initialized")
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        sys.exit(1)
    
    print("=" * 70)
    
    # Run evaluations
    results = []
    for test_case in test_cases:
        result = evaluate_single_song(agent, test_case)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Evaluation Summary")
    print("=" * 70)
    
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed < total:
        print("\n❌ Failed tests:")
        for r in results:
            if not r["passed"]:
                print(f"  - {r['test_case']}: {r.get('error', 'Unknown error')}")
    
    print("=" * 70)
    
    # Save detailed results
    output_path = Path(__file__).parent / "evaluation_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total,
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_path}")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run_evaluation())



