"""
Voice Validator - Ensures emails match the sales rep's writing style

Validates generated emails against the sales rep's voice guidelines:
- No banned phrases
- Appropriate word count
- Calm, direct tone
- Binary questions

Usage:
    from voice_validator import VoiceValidator

    validator = VoiceValidator()
    issues = validator.validate(subject, body)
"""

from typing import List, Dict, Optional
import re


class VoiceValidator:
    """
    Validates emails against the sales rep's voice and style guidelines.
    """

    # Banned phrases (corporate speak and filler)
    BANNED_PHRASES = [
        # Check-in language
        "circle back", "circling back",
        "check in", "checking in",
        "touch base", "touching base",
        "hope this finds you well",

        # Corporate buzzwords
        "synergies", "synergy",
        "transformational",
        "best-in-class",
        "cutting edge", "cutting-edge",
        "world-class",

        # Professional voice avoidances
        "no rush",
        "shaping", "structuring",
        "harmonization",

        # Sales clichés
        "reaching out",
        "wanted to reach out",
        "quick question",
        "on your radar",
        "at your earliest convenience"
    ]

    # Voice principles
    VOICE_PRINCIPLES = {
        "brevity": {
            "word_count_min": 50,
            "word_count_max": 100,
            "sentence_target": (3, 5)
        },
        "directness": {
            "requires_question": True,  # Should have at least one question
            "offer_based_cta": True     # CTA should offer something
        }
    }

    def validate(
        self,
        subject: str,
        body: str,
        constraints: Optional[Dict] = None
    ) -> List[str]:
        """
        Validate email against the sales rep's voice.

        Args:
            subject: Email subject line
            body: Email body text
            constraints: Optional constraints dict with word_count_min/max,
                        sentence_count_min/max, subject_word_max, banned_phrases.
                        If None, uses default values from VOICE_PRINCIPLES.

        Returns:
            List of issues (empty if passes)
        """
        issues = []

        # Use constraints if provided, otherwise use defaults
        if constraints is None:
            constraints = {
                'word_count_min': self.VOICE_PRINCIPLES['brevity']['word_count_min'],
                'word_count_max': self.VOICE_PRINCIPLES['brevity']['word_count_max'],
                'sentence_count_min': self.VOICE_PRINCIPLES['brevity']['sentence_target'][0],
                'sentence_count_max': self.VOICE_PRINCIPLES['brevity']['sentence_target'][1],
                'subject_word_max': 7,
                'banned_phrases': self.BANNED_PHRASES
            }

        # Check banned phrases
        body_lower = body.lower()
        banned_phrases = constraints.get('banned_phrases', self.BANNED_PHRASES)
        for phrase in banned_phrases:
            if phrase in body_lower:
                issues.append(f"Contains banned phrase: '{phrase}'")

        # Check word count
        word_count = len(body.split())
        word_min = constraints.get('word_count_min', 50)
        word_max = constraints.get('word_count_max', 100)

        if word_count < word_min:
            issues.append(f"Too short: {word_count} words (target: {word_min}-{word_max})")
        elif word_count > word_max:
            issues.append(f"Too long: {word_count} words (target: {word_min}-{word_max})")

        # Check sentence count
        sentence_count = body.count('.') + body.count('?')
        sentence_min = constraints.get('sentence_count_min', 3)
        sentence_max = constraints.get('sentence_count_max', 5)

        if sentence_count < sentence_min:
            issues.append(f"Too few sentences: {sentence_count} (target: {sentence_min}-{sentence_max})")
        elif sentence_count > sentence_max:
            issues.append(f"Too many sentences: {sentence_count} (target: {sentence_min}-{sentence_max})")

        # Check for question
        if '?' not in body:
            issues.append("No question found - emails should have qualifying question or binary CTA")

        # Check tone indicators
        exclamation_count = body.count('!')
        if exclamation_count > 0:
            issues.append(f"Too enthusiastic: {exclamation_count} exclamation marks (professional tone avoids these)")

        # Check subject length
        subject_words = len(subject.split())
        subject_max = constraints.get('subject_word_max', 7)

        if subject_words > subject_max:
            issues.append(f"Subject too long: {subject_words} words (target: 1-{subject_max} words)")

        return issues

    def validate_component(self, text: str, component_type: str) -> List[str]:
        """
        Validate individual component text.

        Args:
            text: Component text
            component_type: "pain", "trigger", "cta"

        Returns:
            List of issues
        """
        issues = []

        # Check banned phrases
        text_lower = text.lower()
        for phrase in self.BANNED_PHRASES:
            if phrase in text_lower:
                issues.append(f"{component_type} contains banned phrase: '{phrase}'")

        # Type-specific checks
        if component_type == "pain":
            word_count = len(text.split())
            if word_count < 25 or word_count > 40:
                issues.append(f"Pain text should be 25-40 words, got {word_count}")

        elif component_type == "trigger":
            word_count = len(text.split())
            if word_count < 15 or word_count > 25:
                issues.append(f"Trigger text should be 15-25 words, got {word_count}")

        elif component_type == "cta":
            if "want" not in text_lower and "should i" not in text_lower and "open to" not in text_lower:
                issues.append("CTA should use offer language: 'Want...?', 'Should I...?', or 'Open to...?'")

            if "or not" not in text_lower and "or is" not in text_lower and "or already" not in text_lower:
                issues.append("CTA should include easy 'no' option: 'or not...', 'or is...', 'or already...'")

        return issues
