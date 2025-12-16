"""
Email Assembler - Intelligent email generation from research data

Takes research results and assembles high-relevance emails by:
1. Detecting persona from title
2. Matching pains to persona + industry
3. Finding active regulatory triggers
4. Selecting appropriate CTA
5. Assembling 50-100 word email

Usage:
    from email_assembler import EmailAssembler

    assembler = EmailAssembler()
    email = assembler.generate_email(research_data, contact_name)
"""

from typing import Dict, Optional, Any
import logging
from .email_components import EmailComponentLibrary
from .voice_validator import VoiceValidator

logger = logging.getLogger(__name__)


class EmailAssembler:
    """
    Assembles personalized emails from research using component matching.
    """

    def __init__(self):
        """Initialize email assembler with component library and voice validator."""
        self.library = EmailComponentLibrary()
        self.voice_validator = VoiceValidator()

    def generate_email(
        self,
        research: Dict[str, Any],
        contact_name: str
    ) -> Dict[str, Any]:
        """
        Generate personalized email from research data.

        Args:
            research: Research results with contact, company, perplexity, webfetch
            contact_name: Contact first name for greeting

        Returns:
            {
                'subject': str,
                'body': str,
                'stats': {
                    'word_count': int,
                    'sentence_count': int,
                    'persona_detected': str,
                    'pain_matched': str,
                    'trigger_used': bool
                }
            }
        """
        logger.info(f"Generating email for {contact_name}")

        # Step 1: Detect persona
        contact = research.get('contact') or {}
        title = contact.get('title')
        persona = self.library.detect_persona(title)

        # Step 2: Normalize industry
        company = research.get('company') or {}
        perplexity = research.get('perplexity') or {}
        webfetch = research.get('webfetch') or {}

        raw_industry = (
            company.get('industry') or
            (webfetch.get('industries', [None])[0] if webfetch else None)
        )
        industry = self.library.normalize_industry(raw_industry)

        logger.info(f"Detected: persona={persona}, industry={industry}")

        # Step 3: Get matching pains
        pains = self.library.get_pains(persona, industry, limit=1)

        if not pains:
            logger.warning("No matching pains found, using fallback")
            # Fallback to generic quality pain
            pains = self.library.get_pains("quality", industry, limit=1)

        pain = pains[0]
        logger.info(f"Selected pain: {pain['key']}")

        # Step 4: Check for regulatory triggers
        triggers = self.library.get_triggers(industry)
        trigger = triggers[0] if triggers else None

        if trigger:
            logger.info(f"Using trigger: {trigger['key']}")

        # Step 5: Get matching CTA
        cta = self.library.get_cta(pain['pain_area'], persona)

        if not cta:
            logger.warning("No matching CTA found, using generic")
            cta = {"text": "Want to discuss, or not the right time?"}

        # Step 6: Assemble email
        email_parts = []

        # Add trigger if available
        if trigger:
            email_parts.append(trigger['text'])

        # Add pain text
        email_parts.append(pain['text'])

        # Add qualifying question if available
        if pain.get('question'):
            # Get company name with proper None handling
            contact_data = research.get('contact') or {}
            company_name = contact_data.get('company') or research.get('company_name') or '{{Company}}'
            question = pain['question'].format(company=company_name)
            email_parts.append(question)

        # Add CTA
        email_parts.append(cta['text'])

        # Combine
        body_text = "\n\n".join(email_parts)

        # Step 7: Generate subject line
        subject = self.library.get_subject_line(pain['pain_area'])

        # Step 8: Calculate stats
        word_count = len(body_text.split())
        sentence_count = body_text.count('.') + body_text.count('?')

        # Step 9: Validate voice
        voice_issues = self.voice_validator.validate(subject, body_text)

        stats = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'persona_detected': persona or "unknown",
            'pain_matched': pain['key'],
            'trigger_used': trigger is not None,
            'industry_detected': industry or "unknown",
            'voice_issues': voice_issues  # Add voice validation results
        }

        if voice_issues:
            logger.warning(f"Voice issues detected: {', '.join(voice_issues)}")
        else:
            logger.info(f"Email passed voice validation")

        logger.info(f"Email generated: {word_count} words, {sentence_count} sentences")

        return {
            'subject': subject,
            'body': body_text,
            'stats': stats,
            'components': {
                'trigger': trigger['key'] if trigger else None,
                'pain': pain['key'],
                'cta': pain['pain_area'],
                'persona': persona,
                'industry': industry
            }
        }

    def generate_email_with_override(
        self,
        research: Dict[str, Any],
        contact_name: str,
        persona: Optional[str] = None,
        pain_area: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate email with manual overrides for persona or pain.

        Args:
            research: Research results
            contact_name: Contact first name
            persona: Override detected persona (quality, operations, it, regulatory)
            pain_area: Override pain selection (capa, batch_release, etc.)

        Returns:
            Email dict same as generate_email()
        """
        if persona or pain_area:
            logger.info(f"Using overrides: persona={persona}, pain_area={pain_area}")

        # Detect persona if not overridden
        if not persona:
            contact_data = research.get('contact') or {}
            title = contact_data.get('title')
            persona = self.library.detect_persona(title)

        # Get industry
        company = research.get('company') or {}
        webfetch = research.get('webfetch') or {}
        raw_industry = (
            company.get('industry') or
            (webfetch.get('industries', [None])[0] if webfetch else None)
        )
        industry = self.library.normalize_industry(raw_industry)

        # Get pain (override if specified)
        if pain_area:
            pain_data = next(
                (p for p in self.library.PAIN_LIBRARY.values() if p.get('pain_area') == pain_area),
                None
            )
            if pain_data:
                pains = [pain_data]
            else:
                logger.warning(f"Pain area {pain_area} not found, using default matching")
                pains = self.library.get_pains(persona, industry, limit=1)
        else:
            pains = self.library.get_pains(persona, industry, limit=1)

        if not pains:
            pains = self.library.get_pains("quality", industry, limit=1)

        pain = pains[0]

        # Get trigger
        triggers = self.library.get_triggers(industry)
        trigger = triggers[0] if triggers else None

        # Get CTA
        cta = self.library.get_cta(pain['pain_area'], persona)
        if not cta:
            cta = {"text": "Want to discuss, or not the right time?"}

        # Assemble
        email_parts = []

        if trigger:
            email_parts.append(trigger['text'])

        email_parts.append(pain['text'])

        if pain.get('question'):
            # Get company name with proper None handling
            contact_data = research.get('contact') or {}
            company_name = contact_data.get('company') or research.get('company_name') or '{{Company}}'
            question = pain['question'].format(company=company_name)
            email_parts.append(question)

        email_parts.append(cta['text'])

        body_text = "\n\n".join(email_parts)
        subject = self.library.get_subject_line(pain['pain_area'])

        word_count = len(body_text.split())
        sentence_count = body_text.count('.') + body_text.count('?')

        stats = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'persona_detected': persona or "unknown",
            'pain_matched': pain.get('key', 'unknown'),
            'trigger_used': trigger is not None,
            'industry_detected': industry or "unknown"
        }

        return {
            'subject': subject,
            'body': body_text,
            'stats': stats,
            'components': {
                'trigger': trigger['key'] if trigger else None,
                'pain': pain.get('key', 'unknown'),
                'cta': pain['pain_area'],
                'persona': persona,
                'industry': industry
            }
        }

    def list_available_options(
        self,
        persona: Optional[str] = None,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List available pain points and CTAs for given persona/industry.

        Useful for manual override selection.

        Args:
            persona: Filter by persona
            industry: Filter by industry

        Returns:
            {
                'pains': [list of pain keys],
                'ctas': [list of CTA keys],
                'triggers': [list of trigger keys]
            }
        """
        pains = self.library.get_pains(persona, industry, limit=100)
        triggers = self.library.get_triggers(industry)

        return {
            'pains': [p['key'] for p in pains],
            'pain_areas': list(set(p['pain_area'] for p in pains)),
            'triggers': [t['key'] for t in triggers],
            'personas': list(self.library.PERSONA_PATTERNS.keys()),
            'industries': ['pharma', 'biotech', 'medical_device']
        }


    def build_email_plan(
        self,
        prospect_brief: Dict[str, Any],
        rules_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build email plan with draft text from prospect_brief (hybrid mode).

        This is the NEW hybrid flow - generates actual draft sentences
        that the LLM will rewrite/polish.

        Args:
            prospect_brief: From relevance_engine with persona, signals, constraints
            rules_config: Full rules configuration

        Returns:
            {
                'sentence_1_draft': str,
                'sentence_2_draft': str,
                'sentence_3_draft': str,
                'sentence_4_draft': str,
                'subject_candidates': [str, str, str],
                'selected_components': {...}
            }
        """
        logger.info("Building email plan with draft text (hybrid mode)")

        # Extract from prospect_brief
        persona = prospect_brief.get('persona')
        industry = prospect_brief.get('industry')
        angle_id = prospect_brief.get('angle_id')
        offer_id = prospect_brief.get('offer_id')
        chosen_hook_id = prospect_brief.get('chosen_hook_id')
        verified_signals = prospect_brief.get('verified_signals', [])

        # Get components from library (legacy components used for draft assembly)
        pains = self.library.get_pains(persona, industry, limit=1)
        if not pains:
            pains = self.library.get_pains("quality", industry, limit=1)
        pain = pains[0]

        triggers = self.library.get_triggers(industry)
        trigger = triggers[0] if triggers else None

        cta = self.library.get_cta(pain['pain_area'], persona)
        if not cta:
            cta = {"text": "Want to discuss, or not the right time?"}

        # Build draft sentences (actual text, not just intents)
        sentence_1_draft = ""
        sentence_2_draft = ""
        sentence_3_draft = ""
        sentence_4_draft = ""

        # Sentence 1: Trigger (if available)
        if trigger:
            sentence_1_draft = trigger['text']
            sentence_2_draft = pain['text']
            sentence_3_draft = pain.get('question', "How are you thinking about this?")
            sentence_4_draft = cta['text']
        else:
            # No trigger, start with pain
            sentence_1_draft = pain['text']
            sentence_2_draft = pain.get('question', "How are you thinking about this?")
            sentence_3_draft = cta['text']
            sentence_4_draft = ""  # Only 3 sentences if no trigger

        # Get subject candidates
        subject_candidates = self.library.SUBJECT_LIBRARY.get(
            pain['pain_area'],
            ["Quality initiative"]
        )[:3]  # Top 3 options

        email_plan = {
            'sentence_1_draft': sentence_1_draft,
            'sentence_2_draft': sentence_2_draft,
            'sentence_3_draft': sentence_3_draft,
            'sentence_4_draft': sentence_4_draft,
            'subject_candidates': subject_candidates,
            'selected_components': {
                'trigger_id': trigger['key'] if trigger else None,
                'pain_id': pain['key'],
                'cta_id': pain['pain_area'],
                'angle_id': angle_id,
                'offer_id': offer_id
            }
        }

        logger.info(f"Email plan built with {4 if trigger else 3} draft sentences")

        return email_plan

    def assemble_deterministic_fallback(
        self,
        email_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assemble deterministic email directly from plan (no LLM).

        Used for testing and as fallback when LLM unavailable.
        Simply concatenates the draft sentences.

        Args:
            email_plan: From build_email_plan()

        Returns:
            {
                'subject': str,
                'body': str
            }
        """
        logger.info("Assembling deterministic fallback (no LLM)")

        # Concatenate draft sentences
        sentences = [
            email_plan['sentence_1_draft'],
            email_plan['sentence_2_draft'],
            email_plan['sentence_3_draft'],
        ]

        # Add sentence 4 if present
        if email_plan['sentence_4_draft']:
            sentences.append(email_plan['sentence_4_draft'])

        # Filter empty sentences
        sentences = [s for s in sentences if s]

        # Join with paragraph breaks
        body = "\n\n".join(sentences)

        # Use first subject candidate
        subject = email_plan['subject_candidates'][0]

        return {
            'subject': subject,
            'body': body
        }


class EmailAssemblerError(Exception):
    """Base exception for email assembler errors."""
    pass
