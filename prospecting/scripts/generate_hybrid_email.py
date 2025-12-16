#!/usr/bin/env python3
"""
Generate prospect email using hybrid deterministic + LLM system

Usage:
    python3 scripts/generate_hybrid_email.py \
        --research-json research.json \
        --mode hybrid \
        --tier A \
        --variants 2

    python3 scripts/generate_hybrid_email.py \
        --research-json research.json \
        --mode legacy
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.hybrid_email_generator import HybridEmailGenerator, format_email_output

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print colored header."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}", file=sys.stderr)

def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")

def load_voice_references() -> dict:
    """Load the sales rep's voice reference files."""
    base_path = Path(__file__).parent.parent
    voice_path = base_path / "voice_references"

    voice_refs = {}

    try:
        persona_file = voice_path / "sales_persona.md"
        if persona_file.exists():
            voice_refs['persona'] = persona_file.read_text()

        style_file = voice_path / "writing_style.md"
        if style_file.exists():
            voice_refs['style'] = style_file.read_text()

        questions_file = voice_path / "binary_questions.md"
        if questions_file.exists():
            voice_refs['binary_questions'] = questions_file.read_text()

    except Exception as e:
        print_warning(f"Could not load voice references: {e}")

    return voice_refs

def main():
    """Main email generation workflow."""
    parser = argparse.ArgumentParser(
        description='Generate prospect email using hybrid system'
    )

    # Input
    parser.add_argument(
        '--research-json',
        required=True,
        help='Path to research JSON file or "-" for stdin'
    )

    parser.add_argument(
        '--context-json',
        help='Optional path to synthesized context JSON (from run_prospect_research)'
    )

    # Mode selection
    parser.add_argument(
        '--mode',
        choices=['hybrid', 'legacy'],
        default='hybrid',
        help='Email generation mode (default: hybrid)'
    )

    parser.add_argument(
        '--tier',
        choices=['A', 'B'],
        default='A',
        help='Prospect tier for hybrid mode (default: A)'
    )

    parser.add_argument(
        '--fallback',
        choices=['legacy', 'deterministic'],
        default='legacy',
        help='Fallback mode if hybrid fails (default: legacy)'
    )

    parser.add_argument(
        '--experiment',
        help='Optional experiment name for A/B testing'
    )

    # Output options
    parser.add_argument(
        '--variants',
        type=int,
        default=1,
        help='Number of email variants to generate (default: 1)'
    )

    parser.add_argument(
        '--output-json',
        help='Save full result to JSON file'
    )

    parser.add_argument(
        '--output-email',
        help='Save formatted email to text file'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)

    print_header(f"Hybrid Email Generator - {args.mode.upper()} mode")

    # Load environment
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)

    # Load research data
    try:
        if args.research_json == '-':
            research_data = json.load(sys.stdin)
        else:
            research_path = Path(args.research_json)
            if not research_path.exists():
                print_error(f"Research file not found: {research_path}")
                return 1
            research_data = json.loads(research_path.read_text())

        print_success("Research data loaded")

    except Exception as e:
        print_error(f"Failed to load research data: {e}")
        return 1

    # Load context data (optional)
    context_data = None
    if args.context_json:
        try:
            context_path = Path(args.context_json)
            if not context_path.exists():
                print_error(f"Context file not found: {context_path}")
                return 1
            context_data = json.loads(context_path.read_text())
            print_success("Context data loaded")
        except Exception as e:
            print_error(f"Failed to load context data: {e}")
            return 1

    # Load voice references (for hybrid mode)
    voice_refs = {}
    if args.mode == 'hybrid':
        voice_refs = load_voice_references()
        if voice_refs:
            print_success(f"Loaded {len(voice_refs)} voice reference files")
        else:
            print_warning("No voice references loaded")

    # Initialize generator
    try:
        generator = HybridEmailGenerator(
            mode=args.mode,
            tier=args.tier,
            fallback=args.fallback,
            experiment=args.experiment
        )
        print_success(f"Generator initialized: mode={args.mode}, tier={args.tier}")

    except Exception as e:
        print_error(f"Failed to initialize generator: {e}")
        return 1

    # Generate email(s)
    try:
        result = generator.generate(
            research_data=research_data,
            context_data=context_data,
            voice_refs=voice_refs,
            n_variants=args.variants
        )

        if result is None:
            print_error("Generator returned no result.")
            return 1

        # Extract contact name safely (contact may be null)
        contact = research_data.get('contact') or {}
        contact_name = contact.get('first_name', 'there')

        # Display formatted output
        formatted = format_email_output(result, contact_name)
        print(formatted)

        # Save full result JSON if requested
        if args.output_json:
            output_path = Path(args.output_json)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, indent=2))
            print_success(f"Full result saved to: {output_path}")

        # Save formatted email if requested
        if args.output_email:
            output_path = Path(args.output_email)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(formatted)
            print_success(f"Formatted email saved to: {output_path}")

        # Exit code based on result
        if result['status'] == 'success':
            return 0
        elif result['status'] == 'fallback':
            return 2  # Warning exit code
        elif result['status'] == 'needs_more_research':
            return 3
        else:
            return 1

    except Exception as e:
        print_error(f"Email generation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
