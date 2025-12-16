"""
Hybrid Email Generator - Orchestrates deterministic + LLM email generation

This module ties together all phases of the hybrid system:
1. Load rules configuration
2. Extract signals and build prospect brief (relevance_engine)
3. Generate email plan with draft text (email_assembler)
4. Render variants using LLM (llm_renderer)
5. Validate outputs (validators)

Usage:
    from hybrid_email_generator import HybridEmailGenerator

    generator = HybridEmailGenerator(
        mode="hybrid",  # or "legacy" for old system
        tier="A",       # or "B"
        fallback="legacy"  # fallback mode if hybrid fails
    )

    result = generator.generate(
        research_data=research,
        voice_refs=voice_refs,
        n_variants=2
    )
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .rules_loader import load_rules
from .relevance_engine import build_prospect_brief
from .email_assembler import EmailAssembler
from .llm_renderer import LLMRenderer
from .validators import validate_all
from .quality_controls import ProspectEmailLinter
from .angle_scoring_artifacts import write_angle_scoring_artifact, format_angle_scoring_summary
from .context_quality import (
    compute_prospect_context_quality,
    format_prospect_context_header,
    write_prospect_context_quality_artifact,
    ProspectContextQuality
)

logger = logging.getLogger(__name__)


class HybridEmailGenerator:
    """
    Orchestrates hybrid deterministic + LLM email generation pipeline.
    """

    def __init__(
        self,
        mode: str = "hybrid",
        tier: str = "A",
        fallback: str = "legacy",
        experiment: Optional[str] = None
    ):
        """
        Initialize hybrid email generator.

        Args:
            mode: "hybrid" (new system) or "legacy" (old system)
            tier: "A" (3+ signals) or "B" (2+ signals)
            fallback: Fallback mode if hybrid fails ("legacy" or "deterministic")
            experiment: Optional experiment name for A/B testing rules
        """
        self.mode = mode
        self.tier = tier
        self.fallback = fallback
        self.experiment = experiment

        logger.info(
            f"Initialized HybridEmailGenerator: mode={mode}, tier={tier}, "
            f"fallback={fallback}, experiment={experiment}"
        )

        # Load rules config (cached)
        if mode == "hybrid":
            self.rules_config = load_rules(experiment=experiment, tier=tier)
            logger.info(f"Loaded rules config for tier {tier}")
        else:
            self.rules_config = None

        # Initialize components (some created lazily when needed)
        self.email_assembler = EmailAssembler()
        self.quality_linter = ProspectEmailLinter()

        # LLMRenderer created lazily (needs API key, only used in hybrid mode)
        self._llm_renderer = None

    @property
    def llm_renderer(self):
        """Lazily instantiate LLM renderer (only when needed)."""
        if self._llm_renderer is None:
            self._llm_renderer = LLMRenderer()
        return self._llm_renderer

    def generate(
        self,
        research_data: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None,
        voice_refs: Optional[Dict[str, str]] = None,
        n_variants: int = 1
    ) -> Dict[str, Any]:
        """
        Generate email(s) using specified mode.

        Args:
            research_data: Research results from orchestrator
            voice_refs: Optional voice reference texts for LLM
            n_variants: Number of email variants to generate (hybrid mode only)

        Returns:
            {
                'mode': str,
                'tier': str,
                'status': 'success' | 'fallback' | 'error',
                'variants': [
                    {
                        'subject': str,
                        'body': str,
                        'used_signal_ids': [str],
                        'validation': {...},
                        'quality': {...}
                    }
                ],
                'prospect_brief': {...},  # Only in hybrid mode
                'email_plan': {...},      # Only in hybrid mode
                'fallback_reason': str    # Only if fallback used
            }
        """
        logger.info(f"Generating email in {self.mode} mode")

        if self.mode == "legacy":
            return self._generate_legacy(research_data)
        elif self.mode == "hybrid":
            return self._generate_hybrid(research_data, context_data, voice_refs, n_variants)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

    def _generate_hybrid(
        self,
        research_data: Dict[str, Any],
        context_data: Optional[Dict[str, Any]],
        voice_refs: Optional[Dict[str, str]],
        n_variants: int
    ) -> Dict[str, Any]:
        """
        Generate email using hybrid deterministic + LLM pipeline.

        Returns result dict with status='success' or status='fallback'.
        """
        try:
            # Phase 2: Build prospect brief
            logger.info("Phase 2: Building prospect brief")
            prospect_brief = build_prospect_brief(
                research_data=research_data,
                context=context_data or {},
                tier=self.tier,
                rules_config=self.rules_config
            )

            # Check if needs more research
            if prospect_brief.get('status') == 'needs_more_research':
                logger.warning(
                    f"Insufficient signals for tier {self.tier}: "
                    f"{prospect_brief.get('signals_found', 0)}/{prospect_brief.get('signals_required', 3)} signals found"
                )
                return {
                    'mode': 'hybrid',
                    'tier': self.tier,
                    'status': 'needs_more_research',
                    'variants': [],
                    'prospect_brief': prospect_brief,
                    'signals_found': prospect_brief.get('signals_found', 0),
                    'signals_required': prospect_brief.get('signals_required', 3),
                    # Compat for downstream formatters
                    'signal_count': prospect_brief.get('signals_found', 0),
                    'tier_minimum': prospect_brief.get('signals_required', 3),
                    'reason': prospect_brief.get('reason', 'Insufficient signals'),
                    'recommendations': prospect_brief.get('recommendations', [])
                }

            # Phase 4: Generate email plan with draft text
            logger.info("Phase 4: Generating email plan")
            email_plan = self.email_assembler.build_email_plan(
                prospect_brief=prospect_brief,
                rules_config=self.rules_config
            )

            # Phase 3: Render variants using LLM (fallback if LLM unavailable)
            logger.info(f"Phase 3: Rendering {n_variants} variants with LLM")
            try:
                renderer = self.llm_renderer
            except Exception as e:
                logger.error(f"LLM renderer unavailable: {e}")
                if self.fallback == "legacy":
                    logger.info("Falling back to legacy mode due to missing LLM")
                    result = self._generate_legacy(research_data)
                    result['fallback_reason'] = str(e)
                    result['status'] = 'fallback'
                    return result
                elif self.fallback == "deterministic":
                    logger.info("Falling back to deterministic mode due to missing LLM")
                    return self._generate_deterministic_fallback(
                        prospect_brief,
                        email_plan,
                        fallback_reason=str(e)
                    )
                else:
                    raise

            variants = renderer.render_variants(
                prospect_brief=prospect_brief,
                email_plan=email_plan,
                voice_refs=voice_refs or {},
                n=n_variants,
                rules_config=self.rules_config
            )

            # Validate each variant
            logger.info("Validating variants")
            validated_variants = []

            # Determine confidence mode based on CITED signal count (Fix #4 terminology)
            # Support both new 'cited_signals' and old 'verified_signals' keys
            cited_signals = prospect_brief.get('cited_signals') or prospect_brief.get('verified_signals', [])
            cited_count = sum(
                1 for s in cited_signals
                if s.get('citability') == 'cited' or s.get('verifiability') in ('cited', 'verified')
            )

            # Check for citation format downgrade (Fix #3)
            citation_downgrade = prospect_brief.get('citation_confidence_downgrade', False)

            if citation_downgrade:
                confidence_mode = 'generic'
                logger.warning("Using generic confidence due to citation format issue")
            elif cited_count >= 3:
                confidence_mode = 'high'
            elif cited_count >= 2:
                confidence_mode = 'medium'
            elif cited_count >= 1:
                confidence_mode = 'low'
            else:
                confidence_mode = 'generic'

            logger.info(f"Using confidence_mode='{confidence_mode}' ({cited_count} cited signals)")

            # Extract company name for validation with proper None handling
            company_name = (
                prospect_brief.get('company_name') or
                research_data.get('company_name') or
                (research_data.get('contact') or {}).get('company') or
                (research_data.get('company') or {}).get('name')
            )

            for i, variant in enumerate(variants):
                logger.info(f"Validating variant {i+1}/{len(variants)}")

                # Run all validators with source_type awareness and YAML rules
                validation = validate_all(
                    variant=variant,
                    cited_signals=cited_signals,  # Use new terminology
                    constraints=prospect_brief['constraints'],
                    confidence_mode=confidence_mode,
                    company_name=company_name,
                    rules_config=self.rules_config  # Pass rules config for YAML enforcement
                )

                # Run quality linter
                quality_issues = self.quality_linter.lint(
                    subject=variant['subject'],
                    body=variant['body'],
                    constraints=prospect_brief['constraints']
                )

                # Use new validation result structure
                passed_validation = validation.get('passed', True)

                validated_variants.append({
                    **variant,
                    'validation': validation.get('issues', validation),  # Support both old and new format
                    'quality_issues': quality_issues,
                    'passed_validation': passed_validation,
                    'passed_quality': len(quality_issues) == 0,
                    'confidence_mode': confidence_mode,
                    'citation_warning': prospect_brief.get('citation_warning')  # Include warning in output
                })

                if validated_variants[-1]['passed_validation'] and validated_variants[-1]['passed_quality']:
                    logger.info(f"✓ Variant {i+1} passed all checks")
                else:
                    logger.warning(f"⚠ Variant {i+1} has validation or quality issues")

            # Write angle scoring artifact
            angle_scoring_path = write_angle_scoring_artifact(prospect_brief)

            # Compute context quality for visibility
            context_quality = compute_prospect_context_quality(
                prospect_brief=prospect_brief,
                research_data=research_data
            )
            logger.info(f"Context quality: {context_quality.confidence_mode}, {context_quality.cited_signal_count} cited signals")

            # Write context quality artifact
            context_quality_path = None
            try:
                output_dir = Path('.').resolve() / '.cache' / 'prospects'
                context_quality_path = write_prospect_context_quality_artifact(
                    quality=context_quality,
                    output_dir=str(output_dir)
                )
            except Exception as e:
                logger.warning(f"Failed to write context quality artifact: {e}")

            return {
                'mode': 'hybrid',
                'tier': self.tier,
                'status': 'success',
                'variants': validated_variants,
                'prospect_brief': prospect_brief,
                'email_plan': email_plan,
                'angle_scoring_artifact': str(angle_scoring_path) if angle_scoring_path else None,
                'context_quality': context_quality,
                'context_quality_artifact': context_quality_path
            }

        except Exception as e:
            logger.error(f"Hybrid generation failed: {e}", exc_info=True)

            # Attempt fallback
            if self.fallback == "legacy":
                logger.info("Falling back to legacy mode")
                result = self._generate_legacy(research_data)
                result['fallback_reason'] = str(e)
                result['status'] = 'fallback'
                return result

            elif self.fallback == "deterministic":
                logger.info("Falling back to deterministic mode")
                return self._generate_deterministic_fallback(
                    prospect_brief,
                    email_plan,
                    fallback_reason=str(e)
                )

            else:
                # Return structured error instead of raising
                return {
                    'mode': 'hybrid',
                    'tier': self.tier,
                    'status': 'error',
                    'variants': [],
                    'fallback_reason': str(e)
                }

    def _generate_legacy(
        self,
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate email using legacy system (original email_assembler).

        Returns result dict with single variant.
        """
        logger.info("Generating email using legacy system")

        contact = research_data.get('contact') or {}
        contact_name = contact.get('first_name', 'there')

        # Use legacy generate_email()
        email_result = self.email_assembler.generate_email(
            research=research_data,
            contact_name=contact_name
        )

        # Run quality check
        quality_issues = self.quality_linter.lint(
            subject=email_result['subject'],
            body=email_result['body']
        )

        variant = {
            'subject': email_result['subject'],
            'body': email_result['body'],
            'stats': email_result['stats'],
            'components': email_result['components'],
            'quality_issues': quality_issues,
            'passed_quality': len(quality_issues) == 0
        }

        return {
            'mode': 'legacy',
            'tier': None,
            'status': 'success',
            'variants': [variant]
        }

    def _generate_deterministic_fallback(
        self,
        prospect_brief: Dict[str, Any],
        email_plan: Dict[str, Any],
        fallback_reason: str
    ) -> Dict[str, Any]:
        """
        Generate email using deterministic fallback (no LLM).

        Simply concatenates draft sentences from email_plan.
        """
        logger.info("Generating email using deterministic fallback")

        # Use deterministic assembler
        email_result = self.email_assembler.assemble_deterministic_fallback(
            email_plan=email_plan
        )

        # Run quality check
        quality_issues = self.quality_linter.lint(
            subject=email_result['subject'],
            body=email_result['body'],
            constraints=prospect_brief['constraints']
        )

        variant = {
            'subject': email_result['subject'],
            'body': email_result['body'],
            'used_signal_ids': [],  # Deterministic doesn't track signals
            'quality_issues': quality_issues,
            'passed_quality': len(quality_issues) == 0
        }

        return {
            'mode': 'deterministic',
            'tier': self.tier,
            'status': 'fallback',
            'variants': [variant],
            'prospect_brief': prospect_brief,
            'email_plan': email_plan,
            'fallback_reason': fallback_reason
        }


def format_email_output(result: Dict[str, Any], contact_name: str) -> str:
    """
    Format email generation result for display.

    Args:
        result: Result dict from HybridEmailGenerator.generate()
        contact_name: Contact first name for greeting

    Returns:
        Formatted string for terminal display
    """
    output = []

    # Header
    mode_label = result['mode'].upper()
    status_emoji = {
        'success': '✓',
        'fallback': '⚠',
        'needs_more_research': '⚠',
        'error': '✗'
    }.get(result['status'], '•')

    output.append(f"\n{status_emoji} Email Generation ({mode_label} mode)\n")

    # CONTEXT QUALITY HEADER - Display before email content
    context_quality = result.get('context_quality')
    if context_quality:
        output.append(format_prospect_context_header(context_quality))
        output.append("")  # Blank line after header

    output.append("=" * 60)

    # Check if needs more research
    if result['status'] == 'needs_more_research':
        output.append(f"\n⚠ INSUFFICIENT SIGNALS FOR TIER {result.get('tier', '')}")
        # Accept both legacy and new keys
        found = result.get('signals_found', result.get('signal_count', 0))
        required = result.get('signals_required', result.get('tier_minimum', 0))
        output.append(f"Found: {found} signals")
        output.append(f"Required: {required} signals")
        output.append("\nPlease gather more research data or use Tier B.\n")
        return '\n'.join(output)

    # Fallback warning
    if result['status'] == 'fallback':
        output.append(f"\n⚠ FALLBACK MODE USED")
        output.append(f"Reason: {result.get('fallback_reason', 'Unknown')}\n")

    # Display angle scoring summary (if available)
    prospect_brief = result.get('prospect_brief')
    if prospect_brief and prospect_brief.get('angle_scoring_metadata'):
        scoring_summary = format_angle_scoring_summary(prospect_brief)
        output.append(scoring_summary)
        output.append("")  # Blank line

    # Display variants
    variants = result.get('variants', [])

    for i, variant in enumerate(variants, 1):
        if len(variants) > 1:
            output.append(f"\n--- Variant {i} ---\n")

        # Subject
        output.append(f"Subject: {variant['subject']}\n")

        # Body
        output.append(f"{contact_name},\n")
        output.append(f"{variant['body']}\n")
        output.append("[Your Name]\n")

        # Stats
        word_count = len(variant['body'].split())
        output.append(f"\nWord count: {word_count}")

        # Validation status
        if 'validation' in variant:
            validation = variant['validation']
            passed = variant.get('passed_validation', False)
            status = '✓ PASSED' if passed else '✗ FAILED'
            output.append(f"Validation: {status}")

            if not passed:
                output.append("\nValidation issues:")
                for check, issues in validation.items():
                    if issues:  # issues is a list of strings
                        for issue in issues:
                            output.append(f"  - {check}: {issue}")

        # Quality issues
        quality_issues = variant.get('quality_issues', [])
        if quality_issues:
            output.append("\n⚠ Quality issues:")
            for issue in quality_issues:
                output.append(f"  - {issue}")
        else:
            output.append("Quality: ✓ Passed")

        # Used signals
        if 'used_signal_ids' in variant and variant['used_signal_ids']:
            output.append(f"\nUsed signals: {', '.join(variant['used_signal_ids'])}")

    output.append("\n" + "=" * 60)

    return '\n'.join(output)
