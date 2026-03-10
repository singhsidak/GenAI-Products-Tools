#!/usr/bin/env python3
"""
TuneTrace.AI - Example Usage Script

This script demonstrates how to use TuneTrace.AI for music analysis and recommendations.
"""

import json
import os
import sys

from tune_trace_ai import create_agent


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def example_basic_analysis():
    """Example 1: Basic song analysis."""
    print_section("Example 1: Basic Song Analysis")
    
    agent = create_agent()
    result = agent.analyze_song("Lose Yourself by Eminem")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    # Extract key information
    analysis = result["input_song_analysis"]
    params = analysis["parameters"]
    
    print(f"\n🎵 Song: {analysis['song_name']} by {analysis['artist']}")
    print("\n📊 Key Parameters:")
    print(f"  • Vibe: {params['Intangible Vibe']['value']}")
    print(f"  • Genre: {params['Genre / Subgenre']['value']}")
    print(f"  • Mood: {params['Mood / Tone']['value']}")
    print(f"  • Tempo: {params['Tempo (BPM)']['value']}")
    
    print("\n🎯 Recommendations:")
    for i, rec in enumerate(result["recommendations"], 1):
        is_wildcard = "[WILDCARD]" in rec["rationale"]
        marker = "🎲 " if is_wildcard else ""
        print(f"\n  {i}. {marker}{rec['song_name']} by {rec['artist']}")
        print(f"     {rec['rationale'][:100]}...")


def example_url_analysis():
    """Example 2: Analyze from URL."""
    print_section("Example 2: URL Analysis")
    
    agent = create_agent()
    
    # Using a well-known YouTube URL
    url = "https://www.youtube.com/watch?v=_Yhyp-_hX2s"
    print(f"\n🔗 Analyzing URL: {url}")
    
    result = agent.analyze_song(url)
    
    if "error" in result:
        print(f"⚠️  URL analysis error (this is expected for some URLs)")
        print(f"   Error: {result['error']}")
    else:
        analysis = result.get("input_song_analysis", {})
        print(f"\n✅ Successfully analyzed:")
        print(f"   Song: {analysis.get('song_name', 'Unknown')}")
        print(f"   Artist: {analysis.get('artist', 'Unknown')}")


def example_multiple_songs():
    """Example 3: Analyze multiple songs."""
    print_section("Example 3: Multiple Songs")
    
    agent = create_agent()
    
    songs = """
    Bohemian Rhapsody by Queen
    Smells Like Teen Spirit by Nirvana
    Billie Jean by Michael Jackson
    """
    
    print("\n📝 Analyzing multiple songs...")
    result = agent.analyze_song(songs)
    
    if "multiple_songs" in result:
        print(f"\n✅ Detected and analyzed {result['count']} songs")
        for i, song_result in enumerate(result["results"], 1):
            if "error" not in song_result:
                analysis = song_result.get("input_song_analysis", {})
                print(f"   {i}. {analysis.get('song_name', 'Unknown')}")
    else:
        print("   Processed as single song analysis")


def example_batch_processing():
    """Example 4: Batch processing."""
    print_section("Example 4: Batch Processing")
    
    agent = create_agent()
    
    songs = [
        "Happy by Pharrell Williams",
        "Shape of You by Ed Sheeran",
    ]
    
    print(f"\n📦 Processing batch of {len(songs)} songs...")
    result = agent.analyze_batch(songs)
    
    print(f"\n✅ Batch analysis complete!")
    print(f"   Total: {result['count']} songs")
    
    for item in result["results"]:
        analysis = item.get("analysis", {})
        if "error" not in analysis:
            song_analysis = analysis.get("input_song_analysis", {})
            print(f"   • {song_analysis.get('song_name', 'Unknown')}")


def example_save_results():
    """Example 5: Save results to file."""
    print_section("Example 5: Save Results to JSON File")
    
    agent = create_agent()
    result = agent.analyze_song("Blinding Lights by The Weeknd")
    
    # Save to file
    output_file = "analysis_output.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    print(f"   File size: {os.path.getsize(output_file)} bytes")
    
    # Clean up
    os.remove(output_file)
    print(f"   (Example file removed)")


def main():
    """Run all examples."""
    print("🎵 TuneTrace.AI - Example Usage Demonstrations")
    print("=" * 70)
    
    # Check for API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("\n❌ Error: GOOGLE_API_KEY environment variable not set")
        print("\nPlease set it with:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        print("\nGet your key from: https://aistudio.google.com/app/apikey")
        sys.exit(1)
    
    print("\n✅ API key found. Starting examples...\n")
    
    try:
        # Run examples
        example_basic_analysis()
        example_url_analysis()
        example_multiple_songs()
        example_batch_processing()
        example_save_results()
        
        print_section("Examples Complete!")
        print("\n✨ All examples completed successfully!")
        print("\nNext steps:")
        print("  • Try your own songs: python -m tune_trace_ai.agent 'your song'")
        print("  • Read the docs: README.md and QUICKSTART.md")
        print("  • Run tests: python deployment/test_deployment.py")
        print("  • Check evaluation: python eval/test_eval.py")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error running examples: {e}")
        print("\nThis may be due to:")
        print("  • Network connectivity issues")
        print("  • API rate limits")
        print("  • Invalid API key")
        sys.exit(1)


if __name__ == "__main__":
    main()



