"""
Test RAG + Agents Integration
This file should be in the root folder
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the enhanced orchestrator
from src.orchestrator_enhanced import EnhancedOrchestrator

def test_integration():
    """Test the integrated RAG + Agents system"""
    print("="*60)
    print("🧪 TESTING RAG + AGENTS INTEGRATION")
    print("="*60)
    
    # Initialize orchestrator
    print("\n⏳ Initializing system...")
    try:
        orchestrator = EnhancedOrchestrator()
        print("✅ System initialized successfully")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Run test with a focused topic
    test_topic = "Benefits of AI in Healthcare"
    print(f"\n🔬 Testing with topic: '{test_topic}'")
    print("-"*40)
    
    try:
        result = orchestrator.run_integrated_workflow(
            topic=test_topic,
            audience="general"
        )
        
        # Analyze results
        if result:
            word_count = len(str(result).split())
            char_count = len(str(result))
            
            print("\n" + "="*60)
            print("📊 TEST RESULTS")
            print("="*60)
            print(f"✅ Output generated successfully")
            print(f"📝 Word count: {word_count} words")
            print(f"📝 Character count: {char_count} characters")
            
            if word_count <= 1200:
                print("✅ Within 1200 word limit - GOOD!")
            else:
                print(f"⚠️ Exceeded limit by {word_count - 1200} words")
            
            print("\n📄 Output Preview (first 300 chars):")
            print("-"*40)
            print(str(result)[:300] + "...")
            
        else:
            print("❌ No output generated")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ INTEGRATION TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    print("Starting RAG + Agents Integration Test...")
    print("This will test both systems working together with output limits.\n")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Warning: OPENAI_API_KEY not found in environment")
        print("Make sure your .env file contains: OPENAI_API_KEY=your-key-here\n")
    
    # Run test
    test_integration()
    
    print("\n💡 Check the 'outputs' folder for the generated article!")