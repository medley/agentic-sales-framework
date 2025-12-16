"""
Relevance Engine - Deterministic signal extraction and email plan generation

Responsibilities:
- Detect persona from contact title
- Extract cited signals from research data (REAL citations only)
- Validate tier requirements (tier A needs 3+ signals)
- Select angle and offer based on persona/industry
- Generate email plan with draft text
- Build constraints object

CRITICAL: Signals now have source_type and citability fields:
- source_type: 'public_url' | 'vendor_data' | 'user_provided' | 'inferred'
- citability: 'cited' | 'uncited' | 'generic'

TERMINOLOGY UPDATE (Fix #4):
- "verified" -> "cited" (we confirm citation exists, not truth)
- "verified_signals" -> "cited_signals" (backward compat maintained)
- "verifiability" -> "citability" (backward compat maintained)

Only 'public_url' or 'user_provided' signals can be used for explicit company claims.
'vendor_data' signals (ZoomInfo, etc.) can guide angle selection but must be phrased generically.

Usage:
    from relevance_engine import build_prospect_brief

    prospect_brief = build_prospect_brief(
        research_data=research,
        context=context,
        tier="A",
        rules_config=rules
    )
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)


# Signal source types and their allowed usage
# UPDATED: 'verifiability' renamed to 'citability', 'verified' renamed to 'cited'
SIGNAL_SOURCE_TYPES = {
    'public_url': {
        'description': 'Claim backed by real public URL citation',
        'allow_explicit_claims': True,
        'allow_company_name': True,
        'citability': 'cited'
    },
    'user_provided': {
        'description': 'Claim provided/validated by user',
        'allow_explicit_claims': True,
        'allow_company_name': True,
        'citability': 'cited'
    },
    'vendor_data': {
        'description': 'Data from ZoomInfo, Demandbase, etc. - not publicly citable',
        'allow_explicit_claims': False,
        'allow_company_name': False,  # Must phrase generically
        'citability': 'uncited'
    },
    'inferred': {
        'description': 'Inferred from context, no direct source',
        'allow_explicit_claims': False,
        'allow_company_name': False,
        'citability': 'generic'
    }
}


class RelevanceEngine:
    """
    Deterministic engine for extracting signals and building prospect briefs.

    Supports persona detection with diagnostics and product eligibility enforcement.
    """

    def __init__(self, rules_config: Dict[str, Any]):
        """
        Initialize relevance engine with rules configuration.

        Args:
            rules_config: Loaded rules configuration with personas, angles, offers, constraints
        """
        self.rules_config = rules_config
        # Store last persona diagnostics for inspection
        self._last_persona_diagnostics: Optional[Dict[str, Any]] = None

    def detect_persona(self, title: Optional[str]) -> Optional[str]:
        """
        Detect persona from contact title using rules_config persona patterns.

        Args:
            title: Job title (e.g., "VP Quality")

        Returns:
            Persona key (quality, manufacturing, operations, it, digital, assets, regulatory) or default
        """
        diagnostics = self.detect_persona_with_diagnostics(title)
        return diagnostics['selected_persona']

    def detect_persona_with_diagnostics(self, title: Optional[str]) -> Dict[str, Any]:
        """
        Detect persona from title and return full diagnostics object.

        AMBIGUITY CONSTRAINTS (when ambiguity_detected is True):
        - eligible_products: Intersection of eligible_products across matched personas
        - secondary_products: Empty (conservative approach)
        - safe_angle_only: True (forces safe_angle selection)
        - confidence_downgrade: True (confidence should be downgraded one level)

        Args:
            title: Job title (e.g., "VP Quality")

        Returns:
            Persona diagnostics dict with:
            - input_title: Original title
            - matched_rules: List of all matching persona/pattern pairs
            - selected_persona: Final persona chosen
            - selection_reason: Why this persona was selected
            - ambiguity_detected: True if multiple personas matched
            - ambiguity_note: Explanation if ambiguous
            - fallback_applied: True if default persona was used
            - eligible_products: Products this persona can receive messaging about
            - secondary_products: Products that can be mentioned as related benefit
            - forbidden_products: Products that must NEVER be referenced
            - safe_angle_only: True if only safe_angle should be used (ambiguity constraint)
            - confidence_downgrade: True if confidence should be downgraded (ambiguity constraint)
            - automation_allowed: Whether automated email generation is permitted
            - default_confidence_cap: Maximum confidence level for this persona
            - primary_product_motion: Primary product ID and display name
        """
        diagnostics = {
            'input_title': title,
            'matched_rules': [],
            'selected_persona': None,
            'selection_reason': None,
            'ambiguity_detected': False,
            'ambiguity_note': None,
            'fallback_applied': False,
            'eligible_products': [],
            'secondary_products': [],
            'forbidden_products': [],
            # New ambiguity constraint fields
            'safe_angle_only': False,
            'confidence_downgrade': False,
            # New persona risk fields
            'automation_allowed': True,
            'default_confidence_cap': 'high',
            # New visibility fields
            'primary_product_motion': None
        }

        if not title:
            logger.warning("No title provided for persona detection")
            default_config = self._get_default_persona_config()
            diagnostics['selected_persona'] = default_config['persona']
            diagnostics['selection_reason'] = 'no_title_provided'
            diagnostics['fallback_applied'] = True
            diagnostics['eligible_products'] = default_config.get('eligible_products', ['quality_qms'])
            diagnostics['forbidden_products'] = default_config.get('forbidden_products', [])
            diagnostics['automation_allowed'] = default_config.get('automation_allowed', True)
            diagnostics['default_confidence_cap'] = default_config.get('default_confidence_cap', 'medium')
            # Set primary product motion
            if diagnostics['eligible_products']:
                diagnostics['primary_product_motion'] = self._get_product_display_info(
                    diagnostics['eligible_products'][0]
                )
            self._last_persona_diagnostics = diagnostics
            return diagnostics

        title_lower = title.lower()
        personas = self.rules_config.get('personas', {})

        # Collect ALL matching rules (not just first)
        all_matches = []
        for persona, config in personas.items():
            patterns = config.get('patterns', [])
            for pattern in patterns:
                if pattern.lower() in title_lower:
                    all_matches.append({
                        'persona': persona,
                        'pattern': pattern,
                        'position': title_lower.find(pattern.lower())
                    })

        diagnostics['matched_rules'] = all_matches

        if not all_matches:
            # No match - use default
            logger.warning(f"Could not detect persona from title '{title}'")
            default_config = self._get_default_persona_config()
            diagnostics['selected_persona'] = default_config['persona']
            diagnostics['selection_reason'] = 'no_pattern_matched'
            diagnostics['fallback_applied'] = True
            diagnostics['eligible_products'] = default_config.get('eligible_products', ['quality_qms'])
            diagnostics['forbidden_products'] = default_config.get('forbidden_products', [])
            diagnostics['automation_allowed'] = default_config.get('automation_allowed', True)
            diagnostics['default_confidence_cap'] = default_config.get('default_confidence_cap', 'medium')
            # Set primary product motion
            if diagnostics['eligible_products']:
                diagnostics['primary_product_motion'] = self._get_product_display_info(
                    diagnostics['eligible_products'][0]
                )
            logger.info(f"Using default persona: {diagnostics['selected_persona']}")
        else:
            # Check for ambiguity (multiple distinct personas matched)
            matched_personas = list(set(m['persona'] for m in all_matches))

            if len(matched_personas) > 1:
                diagnostics['ambiguity_detected'] = True
                diagnostics['ambiguity_note'] = (
                    f"Multiple personas matched ({', '.join(matched_personas)}). "
                    f"Applying ambiguity constraints."
                )
                logger.warning(f"Ambiguous title '{title}': matched {matched_personas}")

                # Get ambiguity resolution config
                ambiguity_config = self.rules_config.get('ambiguity_resolution', {})
                strategy = ambiguity_config.get('strategy', 'first_match')

                # AMBIGUITY CONSTRAINTS: Apply from config (with defaults)
                diagnostics['safe_angle_only'] = ambiguity_config.get('force_safe_angle', True)
                diagnostics['confidence_downgrade'] = ambiguity_config.get('downgrade_confidence', True)
                diagnostics['ambiguity_strategy'] = strategy

                # Compute intersection of eligible_products across matched personas
                eligible_sets = []
                for persona_name in matched_personas:
                    p_config = personas.get(persona_name, {})
                    eligible_sets.append(set(p_config.get('eligible_products', [])))

                if eligible_sets:
                    intersection = eligible_sets[0]
                    for s in eligible_sets[1:]:
                        intersection = intersection & s
                    diagnostics['eligible_products'] = list(intersection)
                else:
                    diagnostics['eligible_products'] = []

                # Empty secondary_products when ambiguous (per config, default True)
                if ambiguity_config.get('clear_secondary_products', True):
                    diagnostics['secondary_products'] = []

                # Compute union of forbidden_products
                forbidden_union = set()
                for persona_name in matched_personas:
                    p_config = personas.get(persona_name, {})
                    forbidden_union.update(p_config.get('forbidden_products', []))
                diagnostics['forbidden_products'] = list(forbidden_union)

            # Select persona based on strategy
            ambiguity_config = self.rules_config.get('ambiguity_resolution', {})
            strategy = ambiguity_config.get('strategy', 'first_match')

            if len(matched_personas) > 1 and strategy == 'most_restrictive':
                # Select persona with most forbidden products (safest choice)
                persona_forbidden_counts = {
                    p: len(personas.get(p, {}).get('forbidden_products', []))
                    for p in matched_personas
                }
                selected_persona = max(persona_forbidden_counts, key=persona_forbidden_counts.get)
                selected = next(m for m in all_matches if m['persona'] == selected_persona)
                diagnostics['selection_reason'] = 'most_restrictive'
            elif len(matched_personas) > 1 and strategy == 'broadest':
                # Select persona with most eligible products (most messaging options)
                persona_eligible_counts = {
                    p: len(personas.get(p, {}).get('eligible_products', []))
                    for p in matched_personas
                }
                selected_persona = max(persona_eligible_counts, key=persona_eligible_counts.get)
                selected = next(m for m in all_matches if m['persona'] == selected_persona)
                diagnostics['selection_reason'] = 'broadest'
            else:
                # Default: first_match (maintains existing behavior)
                selected = all_matches[0]
                diagnostics['selection_reason'] = 'first_match' if len(matched_personas) > 1 else 'single_match'

            diagnostics['selected_persona'] = selected['persona']

            # Get persona config for selected persona
            persona_config = personas.get(selected['persona'], {})

            # If NOT ambiguous, use persona's full eligibility
            if not diagnostics['ambiguity_detected']:
                diagnostics['eligible_products'] = persona_config.get('eligible_products', [])
                diagnostics['secondary_products'] = persona_config.get('secondary_products', [])
                diagnostics['forbidden_products'] = persona_config.get('forbidden_products', [])

            # Get automation and confidence settings
            diagnostics['automation_allowed'] = persona_config.get('automation_allowed', True)
            diagnostics['default_confidence_cap'] = persona_config.get('default_confidence_cap', 'high')

            # Set primary product motion
            if diagnostics['eligible_products']:
                diagnostics['primary_product_motion'] = self._get_product_display_info(
                    diagnostics['eligible_products'][0]
                )

            logger.info(f"Detected persona: {selected['persona']} from title '{title}'")

        self._last_persona_diagnostics = diagnostics
        return diagnostics

    def _get_product_display_info(self, product_id: str) -> Dict[str, str]:
        """
        Get display info for a product.

        Args:
            product_id: Internal product ID

        Returns:
            Dict with product_id and display_name
        """
        products = self.rules_config.get('products', {})
        product_config = products.get(product_id, {})
        return {
            'product_id': product_id,
            'display_name': product_config.get('display_name', product_id)
        }

    def get_last_persona_diagnostics(self) -> Optional[Dict[str, Any]]:
        """Return diagnostics from the last persona detection call."""
        return self._last_persona_diagnostics

    def _get_default_persona(self) -> str:
        """
        Get default persona when none detected from title.

        Returns persona from default_persona config, or 'quality' as hardcoded fallback.
        """
        return self._get_default_persona_config()['persona']

    def _get_default_persona_config(self) -> Dict[str, Any]:
        """
        Get default persona configuration when none detected.

        Returns dict with persona, eligible_products, forbidden_products.
        """
        default_config = self.rules_config.get('default_persona', {})
        if default_config and 'persona' in default_config:
            return {
                'persona': default_config['persona'],
                'eligible_products': default_config.get('eligible_products', ['qx']),
                'forbidden_products': default_config.get('forbidden_products', []),
                'reason': default_config.get('reason', 'default fallback')
            }

        # Hardcoded fallback if no default_persona in config
        return {
            'persona': 'quality',
            'eligible_products': ['qx'],
            'forbidden_products': ['mx', 'ax'],
            'reason': 'hardcoded fallback - quality is safest'
        }

    def get_persona_product_eligibility(self, persona: str) -> Dict[str, List[str]]:
        """
        Get product eligibility for a persona.

        Args:
            persona: Persona key

        Returns:
            Dict with eligible_products, secondary_products, forbidden_products
        """
        personas = self.rules_config.get('personas', {})
        persona_config = personas.get(persona, {})

        return {
            'eligible_products': persona_config.get('eligible_products', []),
            'secondary_products': persona_config.get('secondary_products', []),
            'forbidden_products': persona_config.get('forbidden_products', [])
        }

    def is_product_eligible(self, persona: str, product: str) -> bool:
        """
        Check if a product is eligible for a persona.

        Args:
            persona: Persona key
            product: Product key (qx, mx, px, ax, rx)

        Returns:
            True if product is in eligible_products or secondary_products
        """
        eligibility = self.get_persona_product_eligibility(persona)
        return product in eligibility['eligible_products'] or product in eligibility['secondary_products']

    def is_product_forbidden(self, persona: str, product: str) -> bool:
        """
        Check if a product is forbidden for a persona.

        Args:
            persona: Persona key
            product: Product key (qx, mx, px, ax, rx)

        Returns:
            True if product is in forbidden_products
        """
        eligibility = self.get_persona_product_eligibility(persona)
        return product in eligibility['forbidden_products']

    def _get_default_angle_id(self) -> str:
        """
        Get default angle when no match found.

        Returns first angle from config, or 'operational_efficiency' as fallback.
        """
        angles = self.rules_config.get('angles', {})
        if angles:
            return list(angles.keys())[0]
        return 'operational_efficiency'  # Hardcoded fallback

    def _get_default_offer_id(self) -> str:
        """
        Get default offer when no match found.

        Returns first offer from config, or 'checklist_capa' as fallback.
        """
        offers = self.rules_config.get('offers', {})
        if offers:
            return list(offers.keys())[0]
        return 'checklist_capa'  # Hardcoded fallback

    def _is_valid_signal_text(self, text: str) -> bool:
        """
        Check if signal text is valid (not placeholder junk or headers).

        Args:
            text: Text to validate

        Returns:
            True if valid, False if placeholder/junk/headers
        """
        if not text or not isinstance(text, str):
            return False

        # Strip whitespace and markdown formatting
        text_stripped = text.strip().lstrip('*').lstrip('#').strip()

        # Reject empty or whitespace-only
        if not text_stripped:
            return False

        # Reject single-character placeholders
        if len(text_stripped) == 1:
            return False

        # Reject common placeholders
        placeholder_values = {'-', 'n', 'n/a', 'na', 'none', 'null', 'unknown', 'tbd', 'todo'}
        if text_stripped.lower() in placeholder_values:
            return False

        # Reject very short strings that are likely garbage
        if len(text_stripped) < 10:  # Signals should be at least 10 chars
            return False

        # Reject section headers (text ending with colon only)
        if text_stripped.endswith(':') and not text_stripped[:-1].endswith('.'):
            return False

        # Reject if it's only bold/italic markers and a short phrase
        if text_stripped.count('*') >= 2 and len(text_stripped.replace('*', '')) < 20:
            return False

        return True

    def extract_signals(
        self,
        research_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract signals from research data with REAL source citation.

        CRITICAL CHANGE: No more fake Google search URLs.
        - Only extract signals with real source_url from Perplexity citations
        - Vendor data (ZoomInfo) marked as 'vendor_data' source_type
        - Inferred signals marked as 'inferred' and cannot be used for explicit claims

        TERMINOLOGY (Fix #4):
        - 'citability' replaces 'verifiability'
        - 'cited' replaces 'verified'
        - Backward compat: both keys are written to signals

        Args:
            research_data: Research data from orchestrator (perplexity, webfetch)
            context: Synthesized context with company profile, triggers

        Returns:
            List of signals with:
            - id: Unique signal identifier
            - claim: The factual claim text
            - source_url: Real URL or empty string (NEVER fake)
            - source_type: 'public_url' | 'vendor_data' | 'user_provided' | 'inferred'
            - citability: 'cited' | 'uncited' | 'generic' (NEW)
            - verifiability: same as citability (DEPRECATED, for backward compat)
            - scope: 'company_specific' | 'industry_wide' | 'regulatory'
            - recency_days: Estimated days since the event
            - signal_type: Category of signal
            - key_terms: List of key terms for semantic validation
        """
        signals = []
        signal_counter = 1

        # PRIORITY 0: Merge company_intel signals first (highest priority, most authoritative)
        if 'company_intel' in research_data and research_data['company_intel']:
            company_intel = research_data['company_intel']

            # Handle both dict and object forms
            if hasattr(company_intel, 'signals'):
                intel_signals = company_intel.signals
            elif isinstance(company_intel, dict):
                intel_signals = company_intel.get('signals', {})
            else:
                intel_signals = {}

            # Merge public_url signals (cited, sayable)
            for source_type in ['public_url', 'user_provided']:
                source_signals = intel_signals.get(source_type, [])
                for intel_signal in source_signals:
                    # Handle both dict and object forms
                    if hasattr(intel_signal, 'to_dict'):
                        sig_data = intel_signal.to_dict()
                    elif isinstance(intel_signal, dict):
                        sig_data = intel_signal
                    else:
                        continue

                    signals.append({
                        'id': f"signal_{signal_counter:03d}",
                        'claim': sig_data.get('claim', ''),
                        'source_url': sig_data.get('source_url', ''),
                        'source_type': sig_data.get('source_type', source_type),
                        'citability': sig_data.get('citability', 'cited'),
                        'verifiability': sig_data.get('citability', 'cited'),  # Backward compat
                        'scope': 'company_specific',
                        'recency_days': sig_data.get('recency_days', 180),
                        'signal_type': f"{sig_data.get('provider', 'company_intel')}_filing",
                        'key_terms': sig_data.get('key_terms', []),
                        '_origin': 'company_intel',
                        '_provider': sig_data.get('provider', 'unknown')
                    })
                    signal_counter += 1
                    logger.info(
                        f"Added company_intel signal: {sig_data.get('claim', '')[:50]}... "
                        f"(provider: {sig_data.get('provider', 'unknown')})"
                    )

            # Merge vendor_data signals (uncited, for angle guidance only)
            for intel_signal in intel_signals.get('vendor_data', []):
                if hasattr(intel_signal, 'to_dict'):
                    sig_data = intel_signal.to_dict()
                elif isinstance(intel_signal, dict):
                    sig_data = intel_signal
                else:
                    continue

                signals.append({
                    'id': f"signal_{signal_counter:03d}",
                    'claim': sig_data.get('claim', ''),
                    'source_url': sig_data.get('source_url', ''),
                    'source_type': 'vendor_data',
                    'citability': 'uncited',
                    'verifiability': 'uncited',
                    'scope': 'company_specific',
                    'recency_days': sig_data.get('recency_days', 180),
                    'signal_type': f"{sig_data.get('provider', 'company_intel')}_data",
                    'key_terms': sig_data.get('key_terms', []),
                    '_origin': 'company_intel',
                    '_provider': sig_data.get('provider', 'unknown')
                })
                signal_counter += 1

            logger.info(f"Merged {signal_counter - 1} signals from company_intel")

        # Check for citation format warnings from Perplexity (Fix #3)
        citation_downgrade = False
        if 'perplexity' in research_data:
            perplexity_data = research_data.get('perplexity', {})
            if isinstance(perplexity_data, dict):
                citation_downgrade = perplexity_data.get('citation_confidence_downgrade', False)
                if citation_downgrade:
                    logger.warning("Citation format issue detected - will use generic confidence")

        # PRIORITY 1: Extract CITED claims from Perplexity (with real URLs)
        if 'perplexity' in research_data and not citation_downgrade:
            perplexity_data = research_data['perplexity']

            if isinstance(perplexity_data, dict):
                # Use the new cited_claims field which has real source URLs
                cited_claims = perplexity_data.get('cited_claims', [])

                for claim_data in cited_claims:
                    claim_text = claim_data.get('claim', '')
                    source_url = claim_data.get('source_url', '')

                    if not self._is_valid_signal_text(claim_text):
                        continue

                    # Only accept real URLs (not search queries)
                    if not source_url or 'google.com/search' in source_url:
                        logger.warning(f"Skipping claim without real URL: {claim_text[:50]}...")
                        continue

                    # Extract key terms for semantic validation
                    key_terms = self._extract_key_terms(claim_text)

                    signals.append({
                        'id': f"signal_{signal_counter:03d}",
                        'claim': claim_text,
                        'source_url': source_url,
                        'source_type': 'public_url',
                        'citability': 'cited',           # NEW terminology
                        'verifiability': 'cited',        # DEPRECATED (backward compat)
                        'scope': 'company_specific',
                        'recency_days': 30,  # Assume recent for cited claims
                        'signal_type': 'perplexity_cited',
                        'key_terms': key_terms
                    })
                    signal_counter += 1
                    logger.info(f"Added cited signal: {claim_text[:50]}... -> {source_url}")

        # PRIORITY 2: Extract from WebFetch data (only if source_url is real)
        if 'webfetch' in research_data:
            webfetch_data = research_data['webfetch']

            if isinstance(webfetch_data, dict):
                source_url = webfetch_data.get('source_url', '')

                # Only use if source_url is a real URL (not search query)
                if source_url and source_url.startswith('http') and 'google.com/search' not in source_url:
                    recent_news = webfetch_data.get('recent_news', [])

                    if isinstance(recent_news, list):
                        for news_item in recent_news[:3]:
                            if isinstance(news_item, str) and self._is_valid_signal_text(news_item):
                                key_terms = self._extract_key_terms(news_item)

                                signals.append({
                                    'id': f"signal_{signal_counter:03d}",
                                    'claim': news_item,
                                    'source_url': source_url,
                                    'source_type': 'public_url',
                                    'citability': 'cited',
                                    'verifiability': 'cited',  # Backward compat
                                    'scope': 'company_specific',
                                    'recency_days': 60,
                                    'signal_type': 'webfetch_news',
                                    'key_terms': key_terms
                                })
                                signal_counter += 1

        # PRIORITY 3: Extract vendor data signals (ZoomInfo, etc.)
        # These CANNOT be used for explicit claims but CAN guide angle selection
        if 'zoominfo' in research_data:
            zoominfo_data = research_data['zoominfo']
            if isinstance(zoominfo_data, dict):
                # Extract industry and tech stack as generic signals
                tech_stack = zoominfo_data.get('tech_stack', [])
                if tech_stack:
                    signals.append({
                        'id': f"signal_{signal_counter:03d}",
                        'claim': f"Uses technology stack including: {', '.join(tech_stack[:5])}",
                        'source_url': '',  # No public URL
                        'source_type': 'vendor_data',
                        'citability': 'uncited',
                        'verifiability': 'uncited',  # Backward compat
                        'scope': 'company_specific',
                        'recency_days': 90,
                        'signal_type': 'tech_stack',
                        'key_terms': tech_stack[:5]
                    })
                    signal_counter += 1

        # PRIORITY 4: Extract from synthesized triggers (only with real URLs)
        triggers = context.get('triggers', [])
        for trigger in triggers:
            trigger_text = trigger.get('text') or trigger.get('description')
            if not self._is_valid_signal_text(trigger_text):
                continue

            source_url = trigger.get('source_url') or trigger.get('source')

            # Determine source_type based on URL presence
            if source_url and source_url.startswith('http') and 'google.com/search' not in source_url:
                source_type = 'public_url'
                citability = 'cited'
            else:
                source_type = 'inferred'
                citability = 'generic'
                source_url = ''  # Clear fake URLs

            # Check for duplicates
            duplicate = any(s['claim'] == trigger_text for s in signals)
            if duplicate:
                continue

            scope = self._determine_scope(trigger.get('type', ''))
            recency_days = self._estimate_recency(trigger)
            key_terms = self._extract_key_terms(trigger_text)

            signals.append({
                'id': f"signal_{signal_counter:03d}",
                'claim': trigger_text,
                'source_url': source_url,
                'source_type': source_type,
                'citability': citability,
                'verifiability': citability,  # Backward compat
                'scope': scope,
                'recency_days': recency_days,
                'signal_type': trigger.get('type', 'trigger'),
                'key_terms': key_terms
            })
            signal_counter += 1

        # Log signal breakdown by type (using new terminology)
        cited_count = sum(1 for s in signals if s['citability'] == 'cited')
        uncited_count = sum(1 for s in signals if s['citability'] == 'uncited')
        generic_count = sum(1 for s in signals if s['citability'] == 'generic')

        logger.info(
            f"Extracted {len(signals)} signals: "
            f"{cited_count} cited (usable for claims), "
            f"{uncited_count} uncited (angle guidance only), "
            f"{generic_count} generic (industry pain only)"
        )

        return signals

    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms from a claim for semantic validation.

        These terms will be checked against the email body to ensure
        the signal was actually used, not just ID-tagged.

        Args:
            text: The claim text

        Returns:
            List of key terms (nouns, proper nouns, numbers)
        """
        # Simple extraction: words that are capitalized, numbers, or > 6 chars
        words = text.split()
        key_terms = []

        for word in words:
            # Clean punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            if not clean_word:
                continue

            # Keep if: capitalized (proper noun), number, or significant length
            if (clean_word[0].isupper() and len(clean_word) > 2) or \
               clean_word.isdigit() or \
               (len(clean_word) > 6 and clean_word.isalpha()):
                key_terms.append(clean_word.lower())

        # Deduplicate and limit
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)

        return unique_terms[:10]  # Max 10 key terms

    def _determine_scope(self, signal_type: str) -> str:
        """
        Determine signal scope from signal type.

        Args:
            signal_type: Type of signal

        Returns:
            Scope: "company_specific" | "industry_wide" | "regulatory"
        """
        signal_type_lower = signal_type.lower()

        if 'regulatory' in signal_type_lower or 'compliance' in signal_type_lower:
            return 'regulatory'
        elif 'company' in signal_type_lower or 'news' in signal_type_lower:
            return 'company_specific'
        else:
            return 'industry_wide'

    def _estimate_recency(self, item: Dict[str, Any]) -> int:
        """
        Estimate recency in days since source (heuristic).

        Args:
            item: Signal item with potential date info

        Returns:
            Estimated days since source
        """
        # Try to find date field
        date_str = item.get('date') or item.get('published') or item.get('timestamp')

        if date_str:
            try:
                # Try parsing common date formats
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y']:
                    try:
                        date_obj = datetime.strptime(str(date_str)[:10], fmt)
                        days_ago = (datetime.now() - date_obj).days
                        return max(0, days_ago)
                    except ValueError:
                        continue
            except Exception as e:
                logger.debug(f"Could not parse date '{date_str}': {e}")

        # Heuristic fallback based on signal type
        signal_type = item.get('type', '').lower()

        if 'regulatory' in signal_type:
            return 180  # Regulatory signals assumed ~6 months
        elif 'news' in signal_type or 'company' in signal_type:
            return 30   # Company news assumed recent (~1 month)
        else:
            return 90   # Default to ~3 months

    def select_angle(
        self,
        signals: List[Dict[str, Any]],
        persona: Optional[str],
        industry: Optional[str],
        company_name: Optional[str] = None,
        persona_diagnostics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Select angle_id based on signals, persona, and industry.

        AMBIGUITY CONSTRAINT: If persona_diagnostics.safe_angle_only is True,
        forces selection of the persona's safe_angle instead of scoring candidates.

        NEW: Supports LLM-based scoring when enabled in config.
        Process:
        1. Check for safe_angle_only constraint (ambiguity handling)
        2. Generate deterministic candidate angles (eligible only)
        3. If LLM scoring enabled and 2+ candidates, score them
        4. Deterministically select best angle using weighted scores

        Args:
            signals: List of verified signals
            persona: Detected persona
            industry: Company industry
            company_name: Company name (for LLM scoring context)
            persona_diagnostics: Persona diagnostics with ambiguity constraints

        Returns:
            {
                'angle_id': str or None,
                'angle_scoring_metadata': {
                    'method': 'deterministic' | 'llm_scored' | 'safe_angle_forced',
                    'candidate_angles': [...],
                    'angle_scores': [...],  # If LLM scored
                    'chosen_reason': str,   # If LLM scored
                    'tie_break_used': bool  # If LLM scored
                } or None
            }
        """
        angles = self.rules_config.get('angles', {})
        personas = self.rules_config.get('personas', {})

        # AMBIGUITY CONSTRAINT: Force safe_angle if safe_angle_only is True
        if persona_diagnostics and persona_diagnostics.get('safe_angle_only', False):
            persona_config = personas.get(persona, {})
            safe_angle = persona_config.get('safe_angle')

            if safe_angle and safe_angle in angles:
                logger.info(f"Ambiguity constraint: forcing safe_angle '{safe_angle}' for persona '{persona}'")
                return {
                    'angle_id': safe_angle,
                    'angle_scoring_metadata': {
                        'method': 'safe_angle_forced',
                        'reason': f"Ambiguity detected - using safe_angle for persona '{persona}'",
                        'ambiguity_detected': True
                    }
                }

        # Step 1: Generate deterministic candidate angles
        candidates = self._generate_candidate_angles(
            angles=angles,
            signals=signals,
            persona=persona,
            industry=industry
        )

        if not candidates:
            logger.warning("No angle matched signals and persona - using default angle")
            # Return default angle when no match (Fix #3: never return None)
            default_angle_id = self._get_default_angle_id()
            return {
                'angle_id': default_angle_id,
                'angle_scoring_metadata': {
                    'method': 'default',
                    'reason': 'No angles matched persona/signals - using default'
                }
            }

        # Step 2: Check if LLM scoring is enabled
        angle_scoring_config = self.rules_config.get('angle_scoring', {})
        enable_scoring = angle_scoring_config.get('enable_angle_scoring', False)

        # Check CLI mode - LLM scoring disabled in CLI mode
        # Use try/except to handle both package and direct imports
        try:
            from .execution_mode import is_cli_mode, WARNING_LLM_API_DISABLED_CLI_MODE
        except ImportError:
            from execution_mode import is_cli_mode, WARNING_LLM_API_DISABLED_CLI_MODE
        cli_mode = is_cli_mode()

        # Only use LLM scoring if:
        # - NOT in CLI mode (API calls disabled)
        # - Enabled in config
        # - 2+ candidates (no point scoring 1)
        # - Company name available (needed for context)
        use_llm_scoring = (
            not cli_mode and
            enable_scoring and
            len(candidates) >= 2 and
            company_name is not None
        )

        if cli_mode and enable_scoring:
            logger.info("CLI mode: LLM angle scoring disabled, using deterministic fallback")

        if use_llm_scoring:
            logger.info(f"Using LLM scoring for {len(candidates)} candidate angles")
            return self._select_angle_with_llm_scoring(
                candidates=candidates,
                signals=signals,
                persona=persona,
                company_name=company_name,
                angle_scoring_config=angle_scoring_config
            )
        else:
            # Deterministic selection (legacy behavior or CLI mode fallback)
            reason = "CLI mode fallback" if cli_mode else "config disabled or single candidate"
            logger.info(f"Using deterministic selection for {len(candidates)} candidate angles ({reason})")
            result = self._select_angle_deterministic(candidates=candidates)

            # Add CLI mode warning to metadata if applicable
            if cli_mode and enable_scoring:
                if 'angle_scoring_metadata' not in result:
                    result['angle_scoring_metadata'] = {}
                result['angle_scoring_metadata']['cli_mode_warning'] = WARNING_LLM_API_DISABLED_CLI_MODE

            return result

    def _generate_candidate_angles(
        self,
        angles: Dict[str, Any],
        signals: List[Dict[str, Any]],
        persona: Optional[str],
        industry: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate deterministic candidate angles with product eligibility enforcement.

        Filters angles by:
        - Must match persona
        - Must match industry
        - Must have signal support
        - CRITICAL: Angle's products must be eligible for persona (not forbidden)
        - Respects personalization policies and constraints

        Returns:
            List of candidate dicts with angle_id, score, name, description, products
        """
        candidates = []

        # Get persona's product eligibility
        persona_eligibility = self.get_persona_product_eligibility(persona) if persona else {
            'eligible_products': [],
            'secondary_products': [],
            'forbidden_products': []
        }

        for angle_id, angle_config in angles.items():
            score = 0

            # Check persona match (required)
            if persona and persona not in angle_config.get('personas', []):
                continue

            # CRITICAL: Check product eligibility
            # Angle's products must have at least one product eligible for this persona
            angle_products = angle_config.get('products', [])
            if angle_products and persona:
                # Check if any angle product is forbidden for this persona
                forbidden_overlap = set(angle_products) & set(persona_eligibility['forbidden_products'])
                if forbidden_overlap:
                    logger.debug(
                        f"Skipping angle '{angle_id}' - products {forbidden_overlap} "
                        f"forbidden for persona '{persona}'"
                    )
                    continue

                # Check if any angle product is eligible for this persona
                eligible_overlap = set(angle_products) & (
                    set(persona_eligibility['eligible_products']) |
                    set(persona_eligibility['secondary_products'])
                )
                if not eligible_overlap:
                    logger.debug(
                        f"Skipping angle '{angle_id}' - no eligible products for persona '{persona}'"
                    )
                    continue

            if persona and persona in angle_config.get('personas', []):
                score += 2

            # Check industry match
            if industry:
                industry_lower = industry.lower()
                for ind in angle_config.get('industries', []):
                    if ind.lower() in industry_lower:
                        score += 2
                        break

            # Check signal type match
            angle_signal_types = angle_config.get('signal_types', [])
            for signal in signals:
                if signal.get('signal_type') in angle_signal_types:
                    score += 1

            # Only include if score > 0 (some relevance)
            if score > 0:
                candidates.append({
                    'angle_id': angle_id,
                    'score': score,
                    'name': angle_config.get('name', angle_id),
                    'description': angle_config.get('description', ''),
                    'pain_areas': angle_config.get('pain_areas', []),
                    'products': angle_products
                })

        # Sort by score (highest first) and limit to max_candidate_angles
        angle_scoring_config = self.rules_config.get('angle_scoring', {})
        max_candidates = angle_scoring_config.get('max_candidate_angles', 5)

        candidates.sort(key=lambda c: c['score'], reverse=True)
        candidates = candidates[:max_candidates]

        logger.info(f"Generated {len(candidates)} candidate angles (product-filtered)")

        return candidates

    def _select_angle_deterministic(
        self,
        candidates: List[Dict[str, Any]],
        fallback_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Select best angle deterministically (legacy behavior).

        Simply picks highest scoring candidate.

        Args:
            candidates: List of candidate angles with scores
            fallback_reason: Optional reason if this is a fallback from LLM
        """
        if not candidates:
            return {
                'angle_id': None,
                'angle_scoring_metadata': None
            }

        # Sort by score (highest first)
        candidates.sort(key=lambda c: c['score'], reverse=True)
        best = candidates[0]

        logger.info(f"Selected angle deterministically: {best['angle_id']} (score: {best['score']})")

        metadata = {
            'method': 'deterministic',
            'candidate_angles': [c['angle_id'] for c in candidates],
            'deterministic_scores': {c['angle_id']: c['score'] for c in candidates}
        }

        if fallback_reason:
            metadata['fallback_reason'] = fallback_reason

        return {
            'angle_id': best['angle_id'],
            'angle_scoring_metadata': metadata
        }

    def _select_angle_with_llm_scoring(
        self,
        candidates: List[Dict[str, Any]],
        signals: List[Dict[str, Any]],
        persona: str,
        company_name: str,
        angle_scoring_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select best angle using LLM scoring + deterministic selection.

        Process:
        1. Call LLM scorer with candidates and signals
        2. If scorer fails, fall back to deterministic
        3. Deterministically select best using weighted scores
        4. Store scoring metadata
        """
        from .llm_angle_scorer import score_angles, select_best_angle, AngleScorerError

        # Prepare candidate list for scorer
        scorer_candidates = [
            {
                'angle_id': c['angle_id'],
                'name': c['name'],
                'description': c['description']
            }
            for c in candidates
        ]

        # Get scoring configuration
        scoring_weights = angle_scoring_config.get('angle_score_weights', {
            'relevance': 0.45,
            'urgency': 0.35,
            'reply_likelihood': 0.20
        })
        # Model from config, env var, or default
        default_model = os.environ.get('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
        model = angle_scoring_config.get('angle_scoring_model', default_model)

        try:
            # Call LLM scorer
            scoring_result = score_angles(
                persona=persona,
                company_name=company_name,
                verified_signals=signals,
                candidate_angles=scorer_candidates,
                scoring_weights=scoring_weights,
                model=model
            )

            if scoring_result['status'] != 'success':
                raise AngleScorerError(scoring_result.get('error', 'Scoring failed'))

            scored_angles = scoring_result['scores']

            if not scored_angles:
                raise AngleScorerError("No scored angles returned")

            # Deterministically select best angle
            deterministic_priorities = angle_scoring_config.get('deterministic_priorities', {})
            selection = select_best_angle(scored_angles, deterministic_priorities)

            logger.info(
                f"Selected angle with LLM scoring: {selection['chosen_angle_id']} "
                f"(weighted_score: {selection['weighted_score']:.2f})"
            )

            return {
                'angle_id': selection['chosen_angle_id'],
                'angle_scoring_metadata': {
                    'method': 'llm_scored',
                    'candidate_angles': [c['angle_id'] for c in candidates],
                    'angle_scores': scored_angles,
                    'chosen_reason': selection['chosen_angle_reason'],
                    'weighted_score': selection['weighted_score'],
                    'tie_break_used': selection['tie_break_used'],
                    'scoring_weights': scoring_weights
                }
            }

        except Exception as e:
            logger.warning(f"LLM angle scoring failed, falling back to deterministic: {e}")
            # Fall back to deterministic selection with reason
            fallback_reason = str(e)
            return self._select_angle_deterministic(candidates, fallback_reason=fallback_reason)

    def select_offer(
        self,
        persona: Optional[str],
        angle_id: Optional[str]
    ) -> Optional[str]:
        """
        Select offer_id based on persona and angle, with product eligibility enforcement.

        CRITICAL: Offers are filtered by product eligibility before scoring.
        Only offers with products eligible for the persona will be considered.

        Args:
            persona: Detected persona
            angle_id: Selected angle

        Returns:
            offer_id or None
        """
        offers = self.rules_config.get('offers', {})

        # Get persona's product eligibility
        persona_eligibility = self.get_persona_product_eligibility(persona) if persona else {
            'eligible_products': [],
            'secondary_products': [],
            'forbidden_products': []
        }

        # Score each offer (with product filtering)
        offer_scores = {}

        for offer_id_candidate, offer_config in offers.items():
            score = 0

            # CRITICAL: Check product eligibility first
            offer_products = offer_config.get('products', [])
            if offer_products and persona:
                # Check if any offer product is forbidden for this persona
                forbidden_overlap = set(offer_products) & set(persona_eligibility['forbidden_products'])
                if forbidden_overlap:
                    logger.debug(
                        f"Skipping offer '{offer_id_candidate}' - products {forbidden_overlap} "
                        f"forbidden for persona '{persona}'"
                    )
                    continue

                # Check if any offer product is eligible for this persona
                eligible_overlap = set(offer_products) & (
                    set(persona_eligibility['eligible_products']) |
                    set(persona_eligibility['secondary_products'])
                )
                if not eligible_overlap:
                    logger.debug(
                        f"Skipping offer '{offer_id_candidate}' - no eligible products for persona '{persona}'"
                    )
                    continue

            # Check persona match
            if persona and persona in offer_config.get('personas', []):
                score += 2

            # Check angle compatibility (via pain_areas overlap)
            if angle_id:
                angles = self.rules_config.get('angles', {})
                angle_config = angles.get(angle_id, {})
                angle_pain_areas = set(angle_config.get('pain_areas', []))
                offer_pain_areas = set(offer_config.get('pain_areas', []))
                if angle_pain_areas & offer_pain_areas:
                    score += 3

            offer_scores[offer_id_candidate] = score

        # Return highest scoring offer
        if offer_scores:
            best_offer = max(offer_scores.items(), key=lambda x: x[1])
            if best_offer[1] > 0:
                logger.info(f"Selected offer: {best_offer[0]} (score: {best_offer[1]}, product-filtered)")
                return best_offer[0]

        # Return default offer when no match (Fix #3: never return None)
        logger.warning("No offer matched persona and angle - using default offer")
        default_offer_id = self._get_default_offer_id()
        return default_offer_id

    def generate_email_plan(
        self,
        signals: List[Dict[str, Any]],
        angle_id: Optional[str],
        offer_id: Optional[str],
        persona: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate email_plan with draft text for LLM to rewrite.

        Args:
            signals: List of verified signals
            angle_id: Selected angle
            offer_id: Selected offer
            persona: Detected persona

        Returns:
            email_plan dict with sentence_X_draft and subject_candidates
        """
        # Get angle and offer configs
        angles = self.rules_config.get('angles', {})
        offers = self.rules_config.get('offers', {})

        angle_config = angles.get(angle_id, {}) if angle_id else {}
        offer_config = offers.get(offer_id, {}) if offer_id else {}

        # Build draft sentences from components
        # Sentence 1: Hook with signal
        sentence_1 = self._build_hook_sentence(signals, angle_config)

        # Sentence 2: Pain point
        sentence_2 = self._build_pain_sentence(angle_config, persona)

        # Sentence 3: Qualifying question
        sentence_3 = self._build_question_sentence(angle_config, offer_config)

        # Sentence 4: CTA with offer
        sentence_4 = self._build_cta_sentence(offer_config)

        # Subject candidates
        subject_candidates = self._build_subject_candidates(angle_config, offer_config)

        email_plan = {
            'sentence_1_draft': sentence_1,
            'sentence_2_draft': sentence_2,
            'sentence_3_draft': sentence_3,
            'sentence_4_draft': sentence_4,
            'subject_candidates': subject_candidates
        }

        logger.info("Generated email plan with 4 draft sentences")
        return email_plan

    def _build_hook_sentence(
        self,
        signals: List[Dict[str, Any]],
        angle_config: Dict[str, Any]
    ) -> str:
        """Build hook sentence using strongest signal."""
        if not signals:
            return "Recent industry trends show increased regulatory focus."

        # Use most recent, company-specific signal if available
        company_signals = [s for s in signals if s['scope'] == 'company_specific']
        if company_signals:
            signal = min(company_signals, key=lambda s: s['recency_days'])
            return signal['claim']

        # Fall back to regulatory or industry signal
        signal = signals[0]
        return signal['claim']

    def _build_pain_sentence(
        self,
        angle_config: Dict[str, Any],
        persona: Optional[str]
    ) -> str:
        """Build pain point sentence."""
        # Use pain text from angle config
        pain_text = angle_config.get('pain_text', '')

        if pain_text:
            return pain_text

        # Fallback generic pain
        if persona == 'quality':
            return "QA teams are pushed to shorten CAPA cycle time, but manual handoffs keep approvals slow."
        elif persona == 'operations':
            return "Operations teams face batch release delays due to manual record review."
        else:
            return "Teams are balancing speed with compliance in quality workflows."

    def _build_question_sentence(
        self,
        angle_config: Dict[str, Any],
        offer_config: Dict[str, Any]
    ) -> str:
        """Build qualifying question sentence."""
        # Use question from angle or offer config
        question = angle_config.get('question') or offer_config.get('question')

        if question:
            return question

        # Fallback generic question
        return "How are you measuring this today?"

    def _build_cta_sentence(self, offer_config: Dict[str, Any]) -> str:
        """Build CTA sentence with offer."""
        cta_text = offer_config.get('cta_text', '')

        if cta_text:
            return cta_text

        # Fallback generic CTA
        deliverable = offer_config.get('deliverable', 'checklist')
        return f"I can send a 1-page {deliverable}. Want it?"

    def _build_subject_candidates(
        self,
        angle_config: Dict[str, Any],
        offer_config: Dict[str, Any]
    ) -> List[str]:
        """Build subject line candidates."""
        subjects = []

        # Add subjects from angle config
        if 'subjects' in angle_config:
            subjects.extend(angle_config['subjects'])

        # Add subjects from offer config
        if 'subjects' in offer_config:
            subjects.extend(offer_config['subjects'])

        # Deduplicate and limit to 3
        subjects = list(dict.fromkeys(subjects))[:3]

        if not subjects:
            subjects = ["Quality initiative", "Compliance update", "Process improvement"]

        return subjects

    def build_constraints(self, tier: str) -> Dict[str, Any]:
        """
        Build constraints object from rules_config for given tier.

        Args:
            tier: Tier ("A" or "B")

        Returns:
            Constraints dict with all validation rules
        """
        # Get tier config
        tiering = self.rules_config.get('tiering', {})
        tier_config = tiering.get(tier, {})

        # Get base constraints
        constraints_config = self.rules_config.get('constraints', {})

        # Merge tier-specific overrides
        constraints = {
            'word_count_min': tier_config.get('word_count_min', constraints_config.get('word_count_min', 50)),
            'word_count_max': tier_config.get('word_count_max', constraints_config.get('word_count_max', 100)),
            'sentence_count_min': tier_config.get('sentence_count_min', constraints_config.get('sentence_count_min', 3)),
            'sentence_count_max': tier_config.get('sentence_count_max', constraints_config.get('sentence_count_max', 4)),
            'subject_word_max': constraints_config.get('subject_word_max', 4),
            'subject_style': constraints_config.get('subject_style', 'lowercase'),
            'must_end_with_question': tier_config.get('must_end_with_question', True),
            'no_meeting_ask': tier_config.get('no_meeting_ask', True),
            'no_product_pitch': tier_config.get('no_product_pitch', True),
            'banned_phrases': constraints_config.get('banned_phrases', [])
        }

        logger.info(f"Built constraints for tier {tier}")
        return constraints


def build_prospect_brief(
    research_data: Dict,
    context: Dict,
    tier: str,
    rules_config: Dict
) -> Dict[str, Any]:
    """
    Main function: Build prospect brief from research data.

    This is the entry point for Phase 2 of the hybrid system.

    TERMINOLOGY (Fix #4):
    - Output uses 'cited_signals' (primary) and 'verified_signals' (backward compat)
    - Uses 'citability' for signal classification

    Args:
        research_data: Research data from orchestrator (perplexity, webfetch, etc.)
        context: Synthesized context from context_synthesizer
        tier: Tier level ("A" or "B")
        rules_config: Loaded rules configuration

    Returns:
        Prospect brief dict with status, signals, angle, offer, email_plan, constraints
    """
    logger.info(f"Building prospect brief for tier {tier}")

    # Initialize engine
    engine = RelevanceEngine(rules_config)

    # 1. Detect persona (accept both raw contact and synthesized contact_profile)
    # Safer contact detection with type checking
    contact = next(
        filter(lambda x: isinstance(x, dict) and x, [
            context.get('contact'),
            context.get('contact_profile'),
            research_data.get('contact')
        ]),
        {}
    )

    # Validate title before persona detection
    title = contact.get('title', '')
    if not title:
        logger.warning("No title found for persona detection")

    # Get persona with full diagnostics (for ambiguity constraints)
    persona_diagnostics = engine.detect_persona_with_diagnostics(title)
    persona = persona_diagnostics['selected_persona']

    # 2. Extract industry and company name with safer type checking
    # First try explicit company_name from research_data (set by research_orchestrator)
    company_name = research_data.get('company_name') or context.get('company_name')

    company = next(
        filter(lambda x: isinstance(x, dict) and x, [
            context.get('company'),
            context.get('company_profile'),
            research_data.get('company')
        ]),
        {}
    )

    industry = company.get('industry')

    # Fall back to nested lookups if explicit company_name not found
    if not company_name:
        company_name = company.get('name') or contact.get('company')
    if not company_name:
        logger.warning("No company name found, using fallback")
        company_name = 'Unknown Company'

    # 3. Extract cited signals (terminology updated)
    signals = engine.extract_signals(research_data, context)

    # 4. Check for citation format warnings (Fix #3)
    citation_warning = None
    citation_downgrade = False
    if 'perplexity' in research_data:
        perplexity_data = research_data.get('perplexity', {})
        if isinstance(perplexity_data, dict):
            citation_warning = perplexity_data.get('citation_warning')
            citation_downgrade = perplexity_data.get('citation_confidence_downgrade', False)

    # 5. Assess confidence tier based on CITED signal count
    # Count only signals with citability='cited'
    cited_signal_count = sum(1 for s in signals if s.get('citability') == 'cited')
    total_signal_count = len(signals)

    # Confidence tier hierarchy for comparison
    CONFIDENCE_HIERARCHY = ['generic', 'low', 'medium', 'high']

    # Force downgrade if citation format issue detected (Fix #3)
    if citation_downgrade:
        confidence_tier = 'generic'
        confidence_note = f'Generic messaging - citation format issue detected. {citation_warning}'
        logger.warning(f"Forcing generic confidence due to citation format issue")
    elif cited_signal_count >= 3:
        confidence_tier = 'high'
        confidence_note = f'Strong personalization with {cited_signal_count} cited signals'
    elif cited_signal_count >= 2:
        confidence_tier = 'medium'
        confidence_note = f'Moderate personalization with {cited_signal_count} cited signals'
    elif cited_signal_count >= 1:
        confidence_tier = 'low'
        confidence_note = f'Light personalization with {cited_signal_count} cited signal'
    else:
        confidence_tier = 'generic'
        confidence_note = 'Generic messaging - no cited signals available'

    # REFINEMENT: Enforce default_confidence_cap from persona
    # If persona has a cap (e.g., regulatory capped at 'medium'), enforce it
    default_cap = persona_diagnostics.get('default_confidence_cap', 'high')
    cap_index = CONFIDENCE_HIERARCHY.index(default_cap) if default_cap in CONFIDENCE_HIERARCHY else 3
    tier_index = CONFIDENCE_HIERARCHY.index(confidence_tier) if confidence_tier in CONFIDENCE_HIERARCHY else 0
    original_tier = confidence_tier

    confidence_capped = False
    if tier_index > cap_index:
        confidence_tier = default_cap
        confidence_capped = True
        confidence_note = f'{confidence_note} (capped to {default_cap} for {persona} persona)'
        logger.info(f"Confidence capped: {original_tier} -> {confidence_tier} (persona cap: {default_cap})")

    # REFINEMENT: Apply ambiguity confidence downgrade if triggered
    # This applies AFTER cap check, so get current tier_index
    current_tier_index = CONFIDENCE_HIERARCHY.index(confidence_tier) if confidence_tier in CONFIDENCE_HIERARCHY else 0
    if persona_diagnostics.get('confidence_downgrade', False):
        # Downgrade one level (regardless of cap)
        if current_tier_index > 0:
            new_tier = CONFIDENCE_HIERARCHY[current_tier_index - 1]
            confidence_note = f'{confidence_note} (downgraded due to persona ambiguity)'
            logger.info(f"Confidence downgraded: {confidence_tier} -> {new_tier} (ambiguity constraint)")
            confidence_tier = new_tier

    logger.info(f"Confidence tier: {confidence_tier} ({cited_signal_count} cited signals)")

    # 6. Select angle and offer (with LLM scoring support and ambiguity constraints)
    angle_selection = engine.select_angle(
        signals, persona, industry, company_name,
        persona_diagnostics=persona_diagnostics
    )
    angle_id = angle_selection['angle_id']
    angle_scoring_metadata = angle_selection['angle_scoring_metadata']

    offer_id = engine.select_offer(persona, angle_id)

    # 7. Generate email plan
    email_plan = engine.generate_email_plan(signals, angle_id, offer_id, persona)

    # 8. Build constraints
    constraints = engine.build_constraints(tier)

    # 9. Choose hook (use first cited signal for now)
    cited_signals = [s for s in signals if s.get('citability') == 'cited']
    chosen_hook_id = cited_signals[0]['id'] if cited_signals else (signals[0]['id'] if signals else None)

    # 10. Determine if manual review is required
    # REFINEMENT: Explicit flag for regulatory and other high-risk personas
    automation_allowed = persona_diagnostics.get('automation_allowed', True)
    ambiguity_detected = persona_diagnostics.get('ambiguity_detected', False)

    # Review required if:
    # - automation_allowed is False (e.g., regulatory persona)
    # - OR ambiguity was detected (multiple personas matched)
    # - OR confidence was capped/downgraded
    review_required = (
        not automation_allowed or
        ambiguity_detected or
        confidence_capped or
        persona_diagnostics.get('confidence_downgrade', False)
    )

    review_reasons = []
    if not automation_allowed:
        review_reasons.append(f"Persona '{persona}' requires manual review (automation_allowed=false)")
    if ambiguity_detected:
        review_reasons.append(f"Persona ambiguity detected: {persona_diagnostics.get('ambiguity_note', '')}")
    if confidence_capped:
        review_reasons.append(f"Confidence capped from {original_tier} to {confidence_tier}")
    if persona_diagnostics.get('confidence_downgrade', False):
        review_reasons.append("Confidence downgraded due to ambiguity")

    prospect_brief = {
        'status': 'ready',
        'confidence_tier': confidence_tier,
        'confidence_note': confidence_note,
        'persona': persona,
        'industry': industry,
        'company_name': company_name,
        # NEW terminology (primary)
        'cited_signals': signals,
        'cited_signal_count': cited_signal_count,
        # DEPRECATED (backward compatibility)
        'verified_signals': signals,
        'signal_count': total_signal_count,
        # Citation status (Fix #3)
        'citation_warning': citation_warning,
        'citation_confidence_downgrade': citation_downgrade,
        # NEW: Persona diagnostics with visibility fields
        'persona_diagnostics': persona_diagnostics,
        # REFINEMENT: Review/automation flags
        'review_required': review_required,
        'review_reasons': review_reasons,
        'automation_allowed': automation_allowed,
        # Other fields
        'chosen_hook_id': chosen_hook_id,
        'angle_id': angle_id,
        'angle_scoring_metadata': angle_scoring_metadata,
        'offer_id': offer_id,
        'email_plan': email_plan,
        'constraints': constraints
    }

    logger.info(f"Prospect brief ready: {confidence_tier} confidence, {cited_signal_count} cited signals, angle={angle_id}")
    return prospect_brief
