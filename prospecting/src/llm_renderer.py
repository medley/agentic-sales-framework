"""
LLM Renderer - Renders email variants from deterministic email plan

Responsibilities:
- Render natural copy from email_plan and cited_signals
- Produce N variants with different phrasing
- Parse used_signal_ids from LLM output for deterministic validation
- Auto-repair loop on validation failure (max 2 attempts)

CRITICAL: Source Type Awareness
- Signals with source_type='public_url' or 'user_provided' CAN be used for explicit claims
- Signals with source_type='vendor_data' or 'inferred' CANNOT be used for explicit claims
- The prompt now clearly separates "citable signals" from "context-only signals"
- LLM must include key terms from any signal it tags with used_signal_ids

TERMINOLOGY (Fix #4):
- 'cited_signals' replaces 'verified_signals' (backward compat maintained)
- 'citability' replaces 'verifiability' in signal checks

CLI Mode Behavior:
    In CLI mode, this renderer is NOT available - use render_and_validate.py instead
    which provides deterministic rendering from draft sentences.

Usage:
    from llm_renderer import render_variants

    variants = render_variants(
        prospect_brief=prospect_brief,
        email_plan=email_plan,
        voice_refs=voice_refs,
        n=3,
        rules_config=rules_config
    )
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class LLMRendererCLIModeError(Exception):
    """Raised when LLMRenderer is used in CLI mode."""
    pass


class LLMRenderer:
    """
    Renders email variants from email plan using Claude API.

    LLM is sandboxed - it can only rewrite/polish draft text,
    not invent new strategy or claims.

    NOT available in CLI mode - use render_and_validate.py instead.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM renderer.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.

        Raises:
            LLMRendererCLIModeError: If called in CLI mode
            ValueError: If API key is missing in headless mode
        """
        # Import execution mode here to avoid circular imports
        # Use try/except to handle both package and direct imports
        try:
            from .execution_mode import is_cli_mode
        except ImportError:
            from execution_mode import is_cli_mode

        if is_cli_mode():
            raise LLMRendererCLIModeError(
                "LLMRenderer is not available in CLI mode. "
                "Use render_and_validate.py for deterministic rendering instead."
            )

        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        # Import Anthropic only in headless mode
        from anthropic import Anthropic
        self.client = Anthropic(api_key=self.api_key)
        # Model configuration - override via ANTHROPIC_MODEL env var
        self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    def render_variants(
        self,
        prospect_brief: Dict[str, Any],
        email_plan: Dict[str, Any],
        voice_refs: Dict[str, Any],
        n: int,
        rules_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Render N email variants from email plan.

        Args:
            prospect_brief: Contains cited_signals (or verified_signals for backward compat), constraints, persona, etc.
            email_plan: Contains draft sentences and subject candidates
            voice_refs: Voice guidelines and examples
            n: Number of variants to generate
            rules_config: Rules configuration

        Returns:
            List of variant dicts:
            [
                {
                    'subject': str,
                    'body': str,
                    'used_signal_ids': List[str],
                    'attempt': int  # Repair attempt number (0 = first try)
                },
                ...
            ]
        """
        logger.info(f"Rendering {n} email variants")

        # Support both new 'cited_signals' and old 'verified_signals' keys
        cited_signals = prospect_brief.get('cited_signals') or prospect_brief.get('verified_signals', [])

        # Build LLM prompt
        prompt = self._build_prompt(
            email_plan=email_plan,
            cited_signals=cited_signals,
            constraints=prospect_brief['constraints'],
            n=n
        )

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,  # Some creativity for variants
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = response.content[0].text
            logger.debug(f"LLM response received: {len(response_text)} chars")

            # Parse variants from response
            variants = self._parse_variants(response_text)

            if len(variants) < n:
                logger.warning(f"Expected {n} variants, got {len(variants)}")

            return variants

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise LLMRendererError(f"Failed to render variants: {e}")

    def repair_variant(
        self,
        variant: Dict[str, Any],
        violations: List[str],
        prospect_brief: Dict[str, Any],
        email_plan: Dict[str, Any],
        attempt: int
    ) -> Dict[str, Any]:
        """
        Attempt to repair a variant that failed validation.

        Args:
            variant: Failed variant
            violations: List of validation issues
            prospect_brief: Original prospect brief
            email_plan: Original email plan
            attempt: Repair attempt number (1 or 2)

        Returns:
            Repaired variant dict
        """
        logger.info(f"Attempting repair #{attempt} for variant with {len(violations)} violations")

        # Support both new 'cited_signals' and old 'verified_signals' keys
        cited_signals = prospect_brief.get('cited_signals') or prospect_brief.get('verified_signals', [])

        # Build repair prompt
        repair_prompt = self._build_repair_prompt(
            variant=variant,
            violations=violations,
            email_plan=email_plan,
            cited_signals=cited_signals,
            constraints=prospect_brief['constraints']
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for repairs
                messages=[{
                    "role": "user",
                    "content": repair_prompt
                }]
            )

            response_text = response.content[0].text

            # Parse repaired variant
            repaired = self._parse_variants(response_text)

            if not repaired:
                logger.error("Repair failed to produce valid variant")
                return variant  # Return original if parsing fails

            # Mark as repaired
            repaired[0]['attempt'] = attempt
            return repaired[0]

        except Exception as e:
            logger.error(f"Error during repair: {e}")
            return variant  # Return original on error

    def _build_prompt(
        self,
        email_plan: Dict[str, Any],
        cited_signals: List[Dict[str, Any]],
        constraints: Dict[str, Any],
        n: int
    ) -> str:
        """
        Build LLM prompt for rendering variants.

        CRITICAL: Separates signals by source_type:
        - CITED signals (public_url, user_provided): Can be used for explicit claims
        - CONTEXT-ONLY signals (vendor_data, inferred): Guide tone but no explicit claims

        TERMINOLOGY (Fix #4): Uses 'cited' instead of 'verified'
        """
        # Separate signals by citability
        cited_signals_text = []
        context_only_signals_text = []

        for signal in cited_signals:
            source_type = signal.get('source_type', 'inferred')
            # Support both new 'citability' and old 'verifiability'
            citability = signal.get('citability') or signal.get('verifiability', 'generic')
            source_url = signal.get('source_url', '')
            key_terms = signal.get('key_terms', [])

            # Format key terms for the prompt
            key_terms_str = f" [Key terms: {', '.join(key_terms[:5])}]" if key_terms else ""

            if source_type in ('public_url', 'user_provided') and citability in ('cited', 'verified'):
                # These CAN be used for explicit claims
                cited_signals_text.append(
                    f"[{signal['id']}] {signal['claim']}{key_terms_str}\n    Source: {source_url}"
                )
            else:
                # These are CONTEXT-ONLY - cannot make explicit claims
                context_only_signals_text.append(
                    f"[{signal['id']}] {signal['claim']} (Context only - no explicit claims)"
                )

        cited_formatted = "\n".join(cited_signals_text) if cited_signals_text else "None available"
        context_formatted = "\n".join(context_only_signals_text) if context_only_signals_text else "None"

        # Format subject candidates
        subject_candidates = ", ".join(email_plan.get('subject_candidates', ['CAPA backlog']))

        # Extract constraints
        word_min = constraints.get('word_count_min', 50)
        word_max = constraints.get('word_count_max', 100)
        sentence_min = constraints.get('sentence_count_min', 3)
        sentence_max = constraints.get('sentence_count_max', 4)

        # Build source-type aware prompt (terminology updated Fix #4)
        prompt = f"""You are rewriting a cold outbound email to a VP or Director in a regulated life sciences company.
You are NOT deciding strategy. Strategy is already chosen. Draft text is already written.
Your job is ONLY to rewrite/polish the draft to sound more natural while keeping all facts intact.

Draft email sentences:
1. {email_plan.get('sentence_1_draft', '')}
2. {email_plan.get('sentence_2_draft', '')}
3. {email_plan.get('sentence_3_draft', '')}
4. {email_plan.get('sentence_4_draft', '')}

Subject options: {subject_candidates}

=== CITED SIGNALS (can make explicit claims, cite these) ===
{cited_formatted}

=== CONTEXT-ONLY SIGNALS (guide tone/angle, but NO explicit claims) ===
{context_formatted}

CRITICAL RULES:
1. You may ONLY make explicit claims (e.g., "your recent X", "I saw that you...") using CITED signals above.
2. Context-only signals can guide the angle but you MUST phrase generically (e.g., "many teams struggle with..." not "your team struggles with...").
3. If you tag a signal in Used_signal_ids, you MUST include key terms from that signal's claim in your email body.
4. Rewrite the draft sentences, do not invent new content.
5. Do not add facts beyond the signals provided.
6. Do not ask for a call, meeting, calendar, or time.
7. Do not pitch product.
8. Keep {word_min} to {word_max} words, {sentence_min} to {sentence_max} sentences.
9. End with a yes or no question tied to the offer.

Output format (strict):

Variant 1:
Subject: …
Body: …
Used_signal_ids: [signal_001, signal_003]

Variant 2:
Subject: …
Body: …
Used_signal_ids: [signal_001, signal_002]

Variant 3:
Subject: …
Body: …
Used_signal_ids: [signal_001]"""

        # Adjust for requested number of variants
        if n != 3:
            lines = prompt.split('\n')
            output_section_start = None
            for i, line in enumerate(lines):
                if line.strip() == "Output format (strict):":
                    output_section_start = i
                    break

            if output_section_start:
                base_prompt = '\n'.join(lines[:output_section_start+2])
                variant_template = "\n\nVariant {i}:\nSubject: …\nBody: …\nUsed_signal_ids: [signal_001]"

                variants_section = ""
                for i in range(1, n + 1):
                    variants_section += variant_template.format(i=i)

                prompt = base_prompt + variants_section

        return prompt

    def _build_repair_prompt(
        self,
        variant: Dict[str, Any],
        violations: List[str],
        email_plan: Dict[str, Any],
        cited_signals: List[Dict[str, Any]],
        constraints: Dict[str, Any]
    ) -> str:
        """
        Build repair prompt for failed variant.
        Source-type aware to guide repairs correctly.

        TERMINOLOGY (Fix #4): Uses 'cited' instead of 'verified'
        """
        # Format violations
        violations_text = "\n".join(f"- {v}" for v in violations)

        # Separate signals by citability for repair guidance
        cited_signals_text = []
        context_only_signals_text = []

        for signal in cited_signals:
            source_type = signal.get('source_type', 'inferred')
            # Support both new 'citability' and old 'verifiability'
            citability = signal.get('citability') or signal.get('verifiability', 'generic')
            key_terms = signal.get('key_terms', [])
            key_terms_str = f" [Key terms: {', '.join(key_terms[:5])}]" if key_terms else ""

            if source_type in ('public_url', 'user_provided') and citability in ('cited', 'verified'):
                cited_signals_text.append(
                    f"[{signal['id']}] {signal['claim']}{key_terms_str}"
                )
            else:
                context_only_signals_text.append(
                    f"[{signal['id']}] {signal['claim']} (Context only)"
                )

        cited_formatted = "\n".join(cited_signals_text) if cited_signals_text else "None"
        context_formatted = "\n".join(context_only_signals_text) if context_only_signals_text else "None"

        prompt = f"""The following email variant failed validation. Fix ONLY the violations listed. Do not change the meaning or add new claims.

Current email:
Subject: {variant.get('subject', '')}
Body: {variant.get('body', '')}

Violations to fix:
{violations_text}

=== CITED SIGNALS (can make explicit claims) ===
{cited_formatted}

=== CONTEXT-ONLY SIGNALS (generic phrasing only) ===
{context_formatted}

Original draft sentences for reference:
1. {email_plan.get('sentence_1_draft', '')}
2. {email_plan.get('sentence_2_draft', '')}
3. {email_plan.get('sentence_3_draft', '')}
4. {email_plan.get('sentence_4_draft', '')}

REPAIR RULES:
- If violation is about "source_type", you're using a context-only signal for explicit claims. Rephrase generically OR remove the claim.
- If violation is about "semantic_guard", you tagged a signal but didn't use its key terms. Either include the key terms or remove the signal ID.
- If violation is about "fake_urls", that signal cannot be used. Remove it from Used_signal_ids.
- {constraints.get('word_count_min', 50)}-{constraints.get('word_count_max', 100)} words
- {constraints.get('sentence_count_min', 3)}-{constraints.get('sentence_count_max', 4)} sentences
- End with yes/no question
- No meeting ask language
- No product pitch

Output format:
Subject: …
Body: …
Used_signal_ids: [signal_001, signal_002]"""

        return prompt

    def _parse_variants(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse variants from LLM response.

        Expected format:
        Variant 1:
        Subject: ...
        Body: ...
        Used_signal_ids: [signal_001, signal_002]

        Returns:
            List of parsed variant dicts
        """
        variants = []

        # Split by "Variant N:" markers
        variant_blocks = re.split(r'Variant\s+\d+:', response_text)

        # Skip first element (text before first variant)
        for block in variant_blocks[1:]:
            variant = self._parse_variant_block(block.strip())
            if variant:
                variants.append(variant)

        return variants

    def _parse_variant_block(self, block: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single variant block.

        Args:
            block: Text block for one variant

        Returns:
            Variant dict or None if parsing fails
        """
        try:
            lines = block.strip().split('\n')

            subject = None
            body = None
            used_signal_ids = []

            # Parse line by line
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                if line.startswith('Subject:'):
                    subject = line[8:].strip()

                elif line.startswith('Body:'):
                    # Body might be multi-line
                    body_lines = [line[5:].strip()]
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith('Used_signal_ids:'):
                        body_lines.append(lines[i].strip())
                        i += 1
                    body = ' '.join(body_lines).strip()
                    continue  # Don't increment i again at end of loop

                elif line.startswith('Used_signal_ids:'):
                    # Extract signal IDs from list format
                    ids_text = line[16:].strip()
                    # Remove brackets and split
                    ids_text = ids_text.strip('[]')
                    if ids_text:
                        used_signal_ids = [
                            sid.strip().strip('"').strip("'")
                            for sid in ids_text.split(',')
                            if sid.strip()
                        ]

                i += 1

            # Validate we got all required fields
            if not subject or not body:
                logger.warning(f"Failed to parse variant: missing subject or body")
                return None

            return {
                'subject': subject,
                'body': body,
                'used_signal_ids': used_signal_ids,
                'attempt': 0  # Initial attempt
            }

        except Exception as e:
            logger.error(f"Error parsing variant block: {e}")
            return None


class LLMRendererError(Exception):
    """Base exception for LLM renderer errors."""
    pass


def render_variants(
    prospect_brief: Dict[str, Any],
    email_plan: Dict[str, Any],
    voice_refs: Dict[str, Any],
    n: int = 3,
    rules_config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function for rendering variants.

    Args:
        prospect_brief: Prospect brief with verified_signals and constraints
        email_plan: Email plan with draft sentences
        voice_refs: Voice reference materials
        n: Number of variants to generate
        rules_config: Rules configuration (optional)

    Returns:
        List of variant dicts
    """
    renderer = LLMRenderer()
    return renderer.render_variants(
        prospect_brief=prospect_brief,
        email_plan=email_plan,
        voice_refs=voice_refs,
        n=n,
        rules_config=rules_config or {}
    )
