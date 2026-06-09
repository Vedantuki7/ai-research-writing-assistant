"""
main.py - Entry point for the Research and Writing Assistant
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import ResearchWritingOrchestrator
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print a nice banner for the application"""
    banner = """
    ============================================================
    🚀 AI-POWERED RESEARCH & WRITING ASSISTANT
    ============================================================
    """
    print(banner)

def main():
    """Main entry point for the application"""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='AI-Powered Research and Writing Assistant'
    )
    parser.add_argument(
        '--topic',
        type=str,
        required=True,
        help='Topic to research and write about'
    )
    parser.add_argument(
        '--audience',
        type=str,
        default='general',
        help='Target audience (general, technical, academic, business)'
    )
    parser.add_argument(
        '--mode',
        type=str,
        default='sequential',
        choices=['sequential', 'hierarchical'],
        help='Execution mode for the crew'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode with minimal processing'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Display configuration
    print(f"📚 Topic: {args.topic}")
    print(f"👥 Audience: {args.audience}")
    print(f"⚙️ Mode: {args.mode}")
    print("============================================================\n")
    
    try:
        # Check for API keys
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("❌ OPENAI_API_KEY not found in environment variables!")
            print("\nPlease set your OpenAI API key in the .env file:")
            print("OPENAI_API_KEY=your_key_here")
            return 1
        
        if not os.getenv("SERPER_API_KEY"):
            logger.warning("⚠️ SERPER_API_KEY not found - web search will be limited")
            print("\nOptional: Add Serper API key for web search:")
            print("SERPER_API_KEY=your_key_here")
        
        # Initialize orchestrator
        print(f"Initializing {args.mode.upper()} execution...")
        orchestrator = ResearchWritingOrchestrator()
        
        # Run the workflow
        result = orchestrator.execute_workflow(
            topic=args.topic,
            audience=args.audience,
            mode=args.mode
        )
        
        # Display success message
        print("\n" + "="*60)
        print("✅ Workflow completed successfully!")
        print("="*60)
        print("\n📄 Output saved to 'outputs' folder")
        print("📊 Logs available in 'workflow.log'")
        
        # Display summary of result
        if result:
            print("\n--- Final Output Preview ---")
            result_str = str(result.raw) if hasattr(result, 'raw') else str(result)
            print(result_str[:500] + "..." if len(result_str) > 500 else result_str)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
        return 1
        
    except Exception as e:
        logger.error(f"❌ Workflow failed: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        print("\n📝 Check 'workflow.log' for detailed error information")
        return 1

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the main function
    sys.exit(main())