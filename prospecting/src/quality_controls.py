"""
ProspectEmailLinter - Email Quality Validation for Sales Voice
==============================================================

Lightweight linter that validates prospecting emails against the
sales rep's writing style guidelines. Returns list of issues (empty if clean).

Validates:
- Body word count: 75-125 words (prospecting range)
- Subject length: ≤7 words
- Exactly 1 question mark
- No banned phrases (corporate speak, filler)
- No product mentions in first touch

Usage:
    from prospecting.src.quality_controls import ProspectEmailLinter

    linter = ProspectEmailLinter()
    issues = linter.lint(
        subject="Quality Initiative Timeline",
        body="I noticed your company's recent FDA 483..."
    )

    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Email passed all checks!")
"""

import re
from typing import List, Dict, Optional


# Banned phrases (corporate speak and filler)
BANNED_PHRASES = [
    # Filler/check-in language
    "circle back",
    "circling back",
    "check in",
    "checking in",
    "touch base",
    "touching base",
    "hope this finds you well",
    "hope you're well",
    "hope you are well",
    "just checking in",
    "just circling back",
    "just touching base",

    # Corporate buzzwords
    "synergies",
    "synergy",
    "transformational",
    "best-in-class",
    "cutting edge",
    "cutting-edge",
    "world-class",
    "industry-leading",
    "market-leading",

    # Professional voice avoidances
    "no rush",
    "shaping",
    "structuring",
    "harmonization",

    # Other common sales clichés
    "reaching out",
    "wanted to reach out",
    "quick question",
    "on your radar",
    "at your earliest convenience",
]

# Product mentions to avoid in first touch (add your company/product names)
PRODUCT_BANNED_FIRST_TOUCH = [
    "your_company",  # Replace with your company name
    "your_product",  # Replace with your product name
    "qms",
    "mes",
    "qx",
    "mx",
    "ax",
    "vxt",
    "platform",
    "solution",
    "software",
    "our product",
    "our system",
    "our tool",
]


class ProspectEmailLinter:
    """
    Lightweight email linter for the sales rep's prospecting voice.

    Validates emails against the sales rep's style guidelines and returns
    a list of specific issues. Empty list = email is clean.
    """

    def __init__(self, is_first_touch: bool = True):
        """
        Initialize the linter.

        Args:
            is_first_touch: If True, applies stricter rules (no product mentions)
        """
        self.is_first_touch = is_first_touch

    def lint(self, subject: str, body: str, constraints: Optional[Dict] = None) -> List[str]:
        """
        Lint email against the sales rep's style guidelines.

        Args:
            subject: Email subject line
            body: Email body text
            constraints: Optional constraints dict with word_count_min/max,
                        sentence_count_min/max, subject_word_max, banned_phrases,
                        no_meeting_ask, no_product_pitch. If None, uses defaults.

        Returns:
            List of issue descriptions. Empty list if email passes all checks.

        Example:
            >>> linter = ProspectEmailLinter()
            >>> issues = linter.lint(
            ...     subject="Hope this finds you well - quick question",
            ...     body="Just checking in to see if you're interested..."
            ... )
            >>> len(issues) > 0
            True
        """
        issues = []

        # Use constraints if provided, otherwise use defaults
        if constraints is None:
            constraints = {
                'word_count_min': 50,
                'word_count_max': 100,
                'sentence_count_min': 3,
                'sentence_count_max': 4,
                'subject_word_max': 7,
                'banned_phrases': BANNED_PHRASES,
                'no_meeting_ask': True,
                'no_product_pitch': self.is_first_touch
            }

        # Check body word count
        word_count = len(body.split())
        word_min = constraints.get('word_count_min', 50)
        word_max = constraints.get('word_count_max', 100)

        if word_count < word_min:
            issues.append(
                f"Body too short: {word_count} words (target: {word_min}-{word_max} words)"
            )
        elif word_count > word_max:
            issues.append(
                f"Body too long: {word_count} words (target: {word_min}-{word_max} words)"
            )

        # Check sentence count
        sentence_count = body.count('.') + body.count('?')
        sentence_min = constraints.get('sentence_count_min', 3)
        sentence_max = constraints.get('sentence_count_max', 4)

        if sentence_count < sentence_min:
            issues.append(
                f"Too few sentences: {sentence_count} (target: {sentence_min}-{sentence_max})"
            )
        elif sentence_count > sentence_max:
            issues.append(
                f"Too many sentences: {sentence_count} (target: {sentence_min}-{sentence_max})"
            )

        # Check subject length
        subject_word_count = len(subject.split())
        subject_max = constraints.get('subject_word_max', 7)

        if subject_word_count > subject_max:
            issues.append(
                f"Subject too long: {subject_word_count} words (max: {subject_max} words)"
            )

        # Check question mark count (exactly 1)
        question_count = body.count('?')
        if question_count == 0:
            issues.append("Missing question mark (need exactly 1)")
        elif question_count > 1:
            issues.append(
                f"Too many question marks: {question_count} (need exactly 1)"
            )

        # Check for banned phrases
        combined = (subject + ' ' + body).lower()
        found_banned = []

        banned_phrases = constraints.get('banned_phrases', BANNED_PHRASES)
        for phrase in banned_phrases:
            if phrase in combined:
                found_banned.append(f'"{phrase}"')

        if found_banned:
            issues.append(
                f"Banned phrases found: {', '.join(found_banned)}"
            )

        # Check for meeting ask language (if no_meeting_ask is True)
        if constraints.get('no_meeting_ask', True):
            meeting_patterns = [
                r'\bmeet\b', r'\bmeeting\b', r'\bcall\b', r'\bcalling\b',
                r'\bcalendar\b', r'\bschedule\b', r'\btime\s+to\s+talk\b',
                r'\btime\s+to\s+chat\b', r'\bgrab\s+time\b', r'\bbook\s+time\b'
            ]
            for pattern in meeting_patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    issues.append(f"Contains meeting ask language (not allowed in email 1)")
                    break

        # Check for product pitch (if no_product_pitch is True)
        if constraints.get('no_product_pitch', self.is_first_touch):
            found_products = []

            for product in PRODUCT_BANNED_FIRST_TOUCH:
                # Use word boundary matching to avoid false positives
                pattern = r'\b' + re.escape(product) + r'\b'
                if re.search(pattern, combined, re.IGNORECASE):
                    found_products.append(f'"{product}"')

            if found_products:
                issues.append(
                    f"Product mentions found: {', '.join(found_products)}"
                )

        return issues

    def validate_and_report(self, subject: str, body: str) -> bool:
        """
        Lint email and print results to console.

        Args:
            subject: Email subject line
            body: Email body text

        Returns:
            True if email passes all checks, False otherwise

        Example:
            >>> linter = ProspectEmailLinter()
            >>> passed = linter.validate_and_report("Good subject", "Good body...")
        """
        issues = self.lint(subject, body)

        if not issues:
            print("✓ Email passed all quality checks!")
            return True
        else:
            print(f"✗ Found {len(issues)} issue(s):")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
            return False


# =============================================================================
# EXAMPLE USAGE & TESTING
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("ProspectEmailLinter - Testing")
    print("="*80)

    # Test Case 1: Good email (consultative style)
    print("\nTEST 1: High-Quality Prospecting Email")
    print("-" * 80)

    linter_good = ProspectEmailLinter(is_first_touch=True)

    subject_good = "Quality Initiative Timeline"
    body_good = """I noticed your recent FDA 483 observations highlighted quality system gaps. Companies in similar situations typically face 6-12 month remediation cycles, and the approach to modernization can significantly impact that timeline. How are you thinking about your remediation strategy?"""

    print(f"Subject: {subject_good}")
    print(f"Body: {body_good}")
    print(f"\nWord count: {len(body_good.split())} words")
    print(f"Subject length: {len(subject_good.split())} words")
    print(f"Question marks: {body_good.count('?')}")

    print("\nLinting results:")
    linter_good.validate_and_report(subject_good, body_good)

    # Test Case 2: Bad email (violations)
    print("\n" + "="*80)
    print("TEST 2: Poor-Quality Email (Multiple Violations)")
    print("-" * 80)

    linter_bad = ProspectEmailLinter(is_first_touch=True)

    subject_bad = "Hope this finds you well - quick question about our platform"
    body_bad = """I hope this email finds you well. Just checking in to see if you're interested in our QMS solution. We have a best-in-class platform that can help you achieve transformational results. Do you have time? Should I circle back?"""

    print(f"Subject: {subject_bad}")
    print(f"Body: {body_bad}")
    print(f"\nWord count: {len(body_bad.split())} words")
    print(f"Subject length: {len(subject_bad.split())} words")
    print(f"Question marks: {body_bad.count('?')}")

    print("\nLinting results:")
    linter_bad.validate_and_report(subject_bad, body_bad)

    # Test Case 3: Edge case - word count boundaries
    print("\n" + "="*80)
    print("TEST 3: Edge Cases - Word Count Boundaries")
    print("-" * 80)

    linter_edge = ProspectEmailLinter(is_first_touch=False)

    # Exactly 75 words (minimum)
    body_75w = " ".join(["word"] * 74) + " test?"
    issues_75 = linter_edge.lint("Test", body_75w)
    print(f"\n75 words: {len(issues_75)} issues")
    if issues_75:
        print(f"  Issues: {issues_75}")

    # Exactly 125 words (maximum)
    body_125w = " ".join(["word"] * 124) + " test?"
    issues_125 = linter_edge.lint("Test", body_125w)
    print(f"125 words: {len(issues_125)} issues")
    if issues_125:
        print(f"  Issues: {issues_125}")

    # 74 words (too short)
    body_74w = " ".join(["word"] * 73) + " test?"
    issues_74 = linter_edge.lint("Test", body_74w)
    print(f"74 words: {len(issues_74)} issues")
    if issues_74:
        print(f"  Issues: {issues_74}")

    # 126 words (too long)
    body_126w = " ".join(["word"] * 125) + " test?"
    issues_126 = linter_edge.lint("Test", body_126w)
    print(f"126 words: {len(issues_126)} issues")
    if issues_126:
        print(f"  Issues: {issues_126}")

    print("\n" + "="*80)
    print("Testing complete!")
    print("="*80 + "\n")
