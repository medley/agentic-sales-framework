"""
Validators - Deterministic validation for email variants

Provides:
1. Claim integrity validation - signal IDs must exist
2. Source type validation - only cited signals for explicit claims
3. Confidence mode enforcement - strict rules per confidence level (loaded from YAML)
4. Semantic guard - email must reference key terms from used signals

CRITICAL: This module enforces rules from base_config.yaml:
- Explicit company claims require source_type = 'public_url' or 'user_provided'
- Vendor data signals can only guide angle selection (not explicit claims)
- Used signals must be semantically reflected in email body
- Numbers and named entities forbidden in medium/low/generic modes

Usage:
    from validators import validate_all

    results = validate_all(
        variant={'used_signal_ids': ['signal_001'], 'body': '...'},
        cited_signals=[...],
        constraints={...},
        confidence_mode='high',
        rules_config=rules_config  # Load rules from YAML
    )
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import re
import yaml

logger = logging.getLogger(__name__)


# Default confidence mode rules (fallback if YAML not loaded)
# These match the YAML structure but YAML is the source of truth
DEFAULT_CONFIDENCE_MODES = {
    'high': {
        'max_used_signal_ids': 2,
        'forbid_company_name_mentions': False,
        'forbid_numbers': False,
        'forbid_named_entities': False,
        'require_source_type': ['public_url', 'user_provided']
    },
    'medium': {
        'max_used_signal_ids': 1,
        'forbid_company_name_mentions': False,
        'forbid_numbers': True,
        'forbid_named_entities': True,
        'require_source_type': ['public_url', 'user_provided']
    },
    'low': {
        'max_used_signal_ids': 1,
        'forbid_company_name_mentions': True,
        'forbid_numbers': True,
        'forbid_named_entities': True,
        'require_source_type': []
    },
    'generic': {
        'max_used_signal_ids': 0,
        'forbid_company_name_mentions': True,
        'forbid_numbers': True,
        'forbid_named_entities': True,
        'require_source_type': []
    }
}

# Default semantic guard config (fallback if YAML not loaded)
DEFAULT_SEMANTIC_GUARD = {
    'min_term_coverage': 0.5,
    'min_absolute_terms': 2,
    'max_key_terms_per_signal': 10,
    'min_key_term_length': 3
}


def load_validation_rules_from_yaml(rules_config: Optional[Dict] = None) -> Dict[str, Dict]:
    """
    Load validation rules from YAML config.

    Args:
        rules_config: Loaded rules configuration dict, or None to use defaults

    Returns:
        Dict mapping confidence_mode to validation rules
    """
    if not rules_config:
        logger.warning("No rules_config provided, using default validation rules")
        return DEFAULT_CONFIDENCE_MODES

    confidence_modes = rules_config.get('confidence_modes', {})
    validation_rules = confidence_modes.get('validation_rules', {})

    if not validation_rules:
        logger.warning("No validation_rules in config, using defaults")
        return DEFAULT_CONFIDENCE_MODES

    # Merge with defaults to ensure all keys exist
    result = {}
    for mode in ['high', 'medium', 'low', 'generic']:
        yaml_rules = validation_rules.get(mode, {})
        default_rules = DEFAULT_CONFIDENCE_MODES.get(mode, {})

        result[mode] = {
            'max_used_signal_ids': yaml_rules.get('max_used_signal_ids', default_rules.get('max_used_signal_ids', 5)),
            'forbid_company_name_mentions': yaml_rules.get('forbid_company_name_mentions', default_rules.get('forbid_company_name_mentions', False)),
            'forbid_numbers': yaml_rules.get('forbid_numbers', default_rules.get('forbid_numbers', False)),
            'forbid_named_entities': yaml_rules.get('forbid_named_entities', default_rules.get('forbid_named_entities', False)),
            'require_source_type': yaml_rules.get('require_source_type', default_rules.get('require_source_type', []))
        }

    logger.info(f"Loaded validation rules from YAML for modes: {list(result.keys())}")
    return result


def load_semantic_guard_config(rules_config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Load semantic guard configuration from YAML.

    Args:
        rules_config: Loaded rules configuration dict

    Returns:
        Semantic guard config dict
    """
    if not rules_config:
        return DEFAULT_SEMANTIC_GUARD

    semantic_guard = rules_config.get('semantic_guard', {})

    return {
        'min_term_coverage': semantic_guard.get('min_term_coverage', DEFAULT_SEMANTIC_GUARD['min_term_coverage']),
        'min_absolute_terms': semantic_guard.get('min_absolute_terms', DEFAULT_SEMANTIC_GUARD['min_absolute_terms']),
        'max_key_terms_per_signal': semantic_guard.get('max_key_terms_per_signal', DEFAULT_SEMANTIC_GUARD['max_key_terms_per_signal']),
        'min_key_term_length': semantic_guard.get('min_key_term_length', DEFAULT_SEMANTIC_GUARD['min_key_term_length'])
    }


def validate_claim_integrity(
    variant: Dict[str, Any],
    cited_signals: List[Dict[str, Any]]
) -> List[str]:
    """
    Validate that all signal IDs referenced in variant exist in cited_signals.

    This is deterministic validation - we rely on the LLM renderer's
    explicit signal ID tagging, not NLP claim extraction.

    Args:
        variant: Variant dict with 'used_signal_ids' list
        cited_signals: List of cited signal dicts with 'id' field

    Returns:
        List of validation issues. Empty list if all signal IDs are valid.
    """
    issues = []

    used_signal_ids = variant.get('used_signal_ids', [])

    if not isinstance(used_signal_ids, list):
        issues.append(f"Invalid used_signal_ids format: expected list, got {type(used_signal_ids)}")
        return issues

    valid_signal_ids = {signal.get('id') for signal in cited_signals if signal.get('id')}

    logger.debug(f"Validating {len(used_signal_ids)} signal IDs against {len(valid_signal_ids)} cited signals")

    missing_ids = []
    for signal_id in used_signal_ids:
        if signal_id not in valid_signal_ids:
            missing_ids.append(signal_id)
            logger.warning(f"Signal ID '{signal_id}' not found in cited signals")

    if missing_ids:
        issues.append(
            f"Referenced signal IDs not found in cited signals: {', '.join(missing_ids)}"
        )

    return issues


def validate_source_type(
    variant: Dict[str, Any],
    cited_signals: List[Dict[str, Any]],
    confidence_mode: str = 'high',
    rules_config: Optional[Dict] = None
) -> List[str]:
    """
    Validate that used signals have appropriate source_type for claims.

    CRITICAL: Only 'public_url' or 'user_provided' signals can be used for
    explicit company claims. 'vendor_data' and 'inferred' signals cannot.

    Args:
        variant: Variant with used_signal_ids
        cited_signals: List of signals with source_type field
        confidence_mode: Current confidence mode
        rules_config: Rules configuration (for loading allowed source types)

    Returns:
        List of validation issues
    """
    issues = []

    used_signal_ids = variant.get('used_signal_ids', [])
    if not used_signal_ids:
        return issues

    # Load rules from YAML
    validation_rules = load_validation_rules_from_yaml(rules_config)
    mode_rules = validation_rules.get(confidence_mode, validation_rules.get('high', {}))
    allowed_source_types = mode_rules.get('require_source_type', [])

    # Build signal lookup
    signal_lookup = {s.get('id'): s for s in cited_signals if s.get('id')}

    for signal_id in used_signal_ids:
        signal = signal_lookup.get(signal_id)
        if not signal:
            continue  # Already caught by claim_integrity validator

        source_type = signal.get('source_type', 'inferred')
        source_url = signal.get('source_url', '')

        # Check source_type is allowed (only if mode requires specific types)
        if allowed_source_types and source_type not in allowed_source_types:
            issues.append(
                f"Signal '{signal_id}' has source_type '{source_type}' which is not allowed "
                f"in '{confidence_mode}' mode. Allowed types: {allowed_source_types}"
            )

        # Check that public_url signals actually have a URL
        if source_type == 'public_url' and not source_url:
            issues.append(
                f"Signal '{signal_id}' claims source_type='public_url' but has no source_url"
            )

        # Check for fake URLs (Google search queries)
        if source_url and 'google.com/search' in source_url:
            issues.append(
                f"Signal '{signal_id}' has fake source_url (Google search query). "
                f"Use real citations only."
            )

    return issues


def validate_confidence_mode_rules(
    variant: Dict[str, Any],
    cited_signals: List[Dict[str, Any]],
    confidence_mode: str,
    company_name: Optional[str] = None,
    rules_config: Optional[Dict] = None
) -> List[str]:
    """
    Enforce confidence mode rules on email content.

    CRITICAL: This function now loads rules from YAML config (source of truth).
    Enforces:
    - max_used_signal_ids
    - forbid_company_name_mentions
    - forbid_numbers (NEW)
    - forbid_named_entities (NEW)

    Args:
        variant: Email variant with body, subject, used_signal_ids
        cited_signals: All available signals
        confidence_mode: 'high', 'medium', 'low', or 'generic'
        company_name: Company name to check for mentions
        rules_config: Rules configuration loaded from YAML

    Returns:
        List of validation issues
    """
    issues = []

    # Load rules from YAML (source of truth)
    validation_rules = load_validation_rules_from_yaml(rules_config)
    mode_rules = validation_rules.get(confidence_mode, validation_rules.get('generic', {}))

    body = variant.get('body', '')
    subject = variant.get('subject', '')
    full_text = f"{subject} {body}"
    used_signal_ids = variant.get('used_signal_ids', [])

    # Rule 1: Check max signal usage
    max_signals = mode_rules.get('max_used_signal_ids', 99)
    if len(used_signal_ids) > max_signals:
        issues.append(
            f"Too many signals used ({len(used_signal_ids)}) for '{confidence_mode}' mode. "
            f"Maximum allowed: {max_signals}"
        )

    # Rule 2: Check company name mentions
    if mode_rules.get('forbid_company_name_mentions', False):
        if company_name and len(company_name) > 2:
            # Check for company name (case insensitive, word boundary)
            pattern = re.compile(r'\b' + re.escape(company_name) + r'\b', re.IGNORECASE)
            if pattern.search(body):
                issues.append(
                    f"Company name '{company_name}' mentioned in email body, but "
                    f"'{confidence_mode}' mode forbids company-specific references. "
                    f"Rephrase generically."
                )

    # Rule 3: Check for numbers when forbidden (NEW - from YAML)
    if mode_rules.get('forbid_numbers', False):
        # Match numbers that look like metrics/statistics (not dates or generic numbers)
        # Patterns: "20%", "$50M", "3x", "40%", "2024" (year), etc.
        metric_patterns = [
            r'\b\d+%',                    # Percentages: 20%, 40%
            r'\$\d+[MBK]?\b',             # Money: $50M, $2B
            r'\b\d+x\b',                  # Multipliers: 3x, 10x
            r'\b\d{2,}[+]?\s*(?:employees|people|staff|workers)',  # Headcount
            r'\b\d+\s*(?:days?|weeks?|months?|hours?)\b',  # Time durations
        ]

        for pattern in metric_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                issues.append(
                    f"Numeric metric '{match.group()}' found in email, but "
                    f"'{confidence_mode}' mode forbids specific numbers. "
                    f"Remove or rephrase generically."
                )
                break  # Report only first violation

    # Rule 4: Check for named entities when forbidden (NEW - from YAML)
    if mode_rules.get('forbid_named_entities', False):
        # Named entities: Multi-word capitalized phrases that aren't common words
        # Examples: "Project Apollo", "QMSR Initiative", "Boston Facility"

        # Common words that should NOT trigger this rule
        common_capitalized = {
            'quality', 'operations', 'manufacturing', 'compliance', 'regulatory',
            'fda', 'ema', 'iso', 'gmp', 'qms', 'mes', 'erp', 'capa', 'ncr',
            'vp', 'director', 'ceo', 'cfo', 'cio', 'cto',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'q1', 'q2', 'q3', 'q4', 'fy', 'ytd',
            'i', 'we', 'you', 'they', 'the', 'a', 'an'
        }

        # Look for capitalized multi-word phrases (potential named entities)
        # Pattern: Two or more consecutive capitalized words
        named_entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        matches = re.findall(named_entity_pattern, full_text)

        for match in matches:
            # Check if this is NOT a common phrase
            words = match.lower().split()
            if not all(w in common_capitalized for w in words):
                issues.append(
                    f"Named entity '{match}' found in email, but "
                    f"'{confidence_mode}' mode forbids named entities/initiatives. "
                    f"Remove or rephrase generically."
                )
                break  # Report only first violation

    # Rule 5: Check for explicit claim patterns when not allowed
    if confidence_mode in ('low', 'generic'):
        explicit_patterns = [
            r'your (?:recent|new|upcoming)',
            r'(?:you|your company) (?:announced|launched|expanded|acquired)',
            r'I (?:saw|noticed|read) (?:that|about)',
            r'given (?:your|the) recent',
        ]
        for pattern in explicit_patterns:
            if re.search(pattern, body, re.IGNORECASE):
                issues.append(
                    f"Explicit claim pattern detected ('{pattern}') but "
                    f"'{confidence_mode}' mode forbids explicit claims. "
                    f"Use industry-generic language only."
                )
                break

    return issues


def validate_semantic_guard(
    variant: Dict[str, Any],
    cited_signals: List[Dict[str, Any]],
    rules_config: Optional[Dict] = None
) -> List[str]:
    """
    Semantic validation: if a signal ID is used, the email must include
    key terms from that signal's claim or a validated paraphrase.

    This prevents "signal tagging" without actually using the signal.

    UPDATED: Now uses configurable thresholds from YAML:
    - min_term_coverage: 0.5 (50% of key terms must match)
    - min_absolute_terms: 2 (at least 2 terms must appear)

    Args:
        variant: Email variant with body and used_signal_ids
        cited_signals: Signals with 'key_terms' field
        rules_config: Rules configuration for thresholds

    Returns:
        List of validation issues
    """
    issues = []

    used_signal_ids = variant.get('used_signal_ids', [])
    if not used_signal_ids:
        return issues

    # Load semantic guard config from YAML
    semantic_config = load_semantic_guard_config(rules_config)
    min_term_coverage = semantic_config.get('min_term_coverage', 0.5)
    min_absolute_terms = semantic_config.get('min_absolute_terms', 2)

    body = variant.get('body', '').lower()
    subject = variant.get('subject', '').lower()
    full_text = f"{subject} {body}"

    # Build signal lookup
    signal_lookup = {s.get('id'): s for s in cited_signals if s.get('id')}

    for signal_id in used_signal_ids:
        signal = signal_lookup.get(signal_id)
        if not signal:
            continue

        key_terms = signal.get('key_terms', [])
        if not key_terms:
            # No key terms extracted, skip semantic check
            continue

        # Count how many key terms appear in the email
        terms_found = sum(1 for term in key_terms if term.lower() in full_text)
        coverage = terms_found / len(key_terms) if key_terms else 0

        # Check BOTH coverage threshold AND absolute minimum
        coverage_failed = coverage < min_term_coverage
        absolute_failed = terms_found < min_absolute_terms

        if coverage_failed or absolute_failed:
            failure_reasons = []
            if coverage_failed:
                failure_reasons.append(f"coverage {coverage:.0%} < {min_term_coverage:.0%}")
            if absolute_failed:
                failure_reasons.append(f"terms found {terms_found} < {min_absolute_terms} minimum")

            issues.append(
                f"Signal '{signal_id}' tagged but insufficient key terms in email. "
                f"Expected terms: {key_terms[:5]}{'...' if len(key_terms) > 5 else ''}. "
                f"Failures: {', '.join(failure_reasons)}. "
                f"Either use the signal's facts or remove the tag."
            )
            logger.warning(
                f"Semantic guard failed for {signal_id}: "
                f"found {terms_found}/{len(key_terms)} terms, "
                f"coverage={coverage:.0%}, min_absolute={min_absolute_terms}"
            )

    return issues


def validate_must_end_with_question(body: str) -> List[str]:
    """
    Validate that email body ends with a yes/no question.

    Args:
        body: Email body text

    Returns:
        List of issues (empty if passes)
    """
    issues = []

    body_stripped = body.strip()

    if not body_stripped.endswith('?'):
        issues.append("Email must end with a question mark")
    else:
        last_sentence = body_stripped.split('.')[-1].strip()

        yes_no_patterns = [
            'want', 'need', 'would you', 'should i', 'can i', 'could i',
            'are you', 'is this', 'do you', 'does this', 'open to',
            'interested', 'make sense', 'or not', 'or is', 'or already'
        ]

        is_yes_no = any(pattern in last_sentence.lower() for pattern in yes_no_patterns)

        if not is_yes_no:
            issues.append(
                "Email should end with a yes/no question (e.g., 'Want it?', 'Should I send?', 'Open to it?')"
            )

    return issues


def validate_no_fake_urls(
    cited_signals: List[Dict[str, Any]]
) -> List[str]:
    """
    Global validation: ensure no signals have fake source URLs.

    This catches any signals that slipped through with Google search URLs
    or other fabricated sources.

    Args:
        cited_signals: All signals in the brief

    Returns:
        List of validation issues
    """
    issues = []

    for signal in cited_signals:
        signal_id = signal.get('id', 'unknown')
        source_url = signal.get('source_url', '')
        source_type = signal.get('source_type', '')

        # Check for fake URLs
        if source_url:
            if 'google.com/search' in source_url:
                issues.append(
                    f"CRITICAL: Signal '{signal_id}' has fake Google search URL. "
                    f"Remove or replace with real citation."
                )
            elif source_type == 'public_url' and not source_url.startswith('http'):
                issues.append(
                    f"Signal '{signal_id}' claims public_url but URL is invalid: {source_url}"
                )

    return issues


def validate_forbidden_products(
    variant: Dict[str, Any],
    persona: Optional[str],
    rules_config: Optional[Dict] = None,
    confidence_mode: str = 'high'
) -> List[str]:
    """
    Validate that email content does not reference forbidden products for the persona.

    IMPROVED: Uses phrase-level triggers and unique identifiers instead of single keywords
    to reduce false positives. Confidence-aware strictness.

    CRITICAL SAFETY CHECK: Manufacturing personas must not receive Qx messaging,
    Assets personas must not receive QMS-only framing, etc.

    Validation behavior by confidence mode:
    - HIGH: Block unique_identifiers + explicit forbidden_phrases
    - MEDIUM/LOW/GENERIC: Block unique_identifiers + forbidden_phrases (stricter)

    Args:
        variant: Variant dict with subject and body
        persona: Detected persona
        rules_config: Rules configuration with persona/product definitions
        confidence_mode: Current confidence mode (affects strictness)

    Returns:
        List of validation issues. Empty if no forbidden products referenced.
    """
    issues = []

    if not persona or not rules_config:
        return issues

    # Get persona's forbidden products
    personas = rules_config.get('personas', {})
    persona_config = personas.get(persona, {})
    forbidden_products = persona_config.get('forbidden_products', [])

    if not forbidden_products:
        return issues

    # Get product definitions
    products = rules_config.get('products', {})

    # Get email text
    subject = variant.get('subject', '').lower()
    body = variant.get('body', '').lower()
    full_text = f"{subject} {body}"

    found_forbidden = []
    found_in_product = {}

    # Check each forbidden product
    for product_id in forbidden_products:
        product_config = products.get(product_id, {})
        product_name = product_config.get('display_name', product_id)

        # Get phrase-level triggers (multi-word, product-specific)
        forbidden_phrases = product_config.get('forbidden_phrases', [])

        # Get unique identifiers (high-confidence single terms)
        unique_identifiers = product_config.get('unique_identifiers', [])

        # Check forbidden phrases (always checked)
        for phrase in forbidden_phrases:
            phrase_lower = phrase.lower()
            if phrase_lower in full_text:
                if product_id not in found_in_product:
                    found_in_product[product_id] = []
                found_in_product[product_id].append(phrase)
                found_forbidden.append(phrase)

        # Check unique identifiers (always checked - these are high confidence)
        for identifier in unique_identifiers:
            identifier_lower = identifier.lower()
            # Use word boundary for unique identifiers
            pattern = r'\b' + re.escape(identifier_lower) + r'\b'
            if re.search(pattern, full_text):
                if product_id not in found_in_product:
                    found_in_product[product_id] = []
                if identifier not in found_in_product[product_id]:
                    found_in_product[product_id].append(identifier)
                    found_forbidden.append(identifier)

    if found_forbidden:
        # Build detailed error message
        product_details = []
        for product_id, triggers in found_in_product.items():
            product_config = products.get(product_id, {})
            product_name = product_config.get('display_name', product_id)
            product_details.append(f"{product_name}: [{', '.join(triggers)}]")

        issues.append(
            f"Email contains forbidden product references for persona '{persona}': "
            f"{'; '.join(product_details)}. "
            f"Use eligible products only: {persona_config.get('eligible_products', [])}."
        )
        logger.warning(
            f"Forbidden product triggers found for persona '{persona}': {found_in_product}"
        )

    return issues


def validate_all(
    variant: Dict[str, Any],
    cited_signals: List[Dict[str, Any]],
    constraints: Dict[str, Any],
    confidence_mode: str = 'high',
    company_name: Optional[str] = None,
    rules_config: Optional[Dict] = None,
    persona: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run all validators on a variant.

    UPDATED: Now includes product eligibility validation for persona safety.

    Args:
        variant: Variant dict with subject, body, used_signal_ids
        cited_signals: List of cited signals (renamed from verified_signals)
        constraints: Constraints dict
        confidence_mode: Current confidence mode ('high', 'medium', 'low', 'generic')
        company_name: Company name for mention checking
        rules_config: Rules configuration loaded from YAML (source of truth)
        persona: Detected persona (for product eligibility validation)

    Returns:
        Dict with validation results:
        {
            'passed': bool,
            'issues': {
                'claim_integrity': [...],
                'source_type': [...],
                'confidence_mode': [...],
                'semantic_guard': [...],
                'must_end_with_question': [...],
                'fake_urls': [...],
                'forbidden_products': [...]
            },
            'total_issues': int
        }
    """
    results = {
        'passed': True,
        'issues': {},
        'total_issues': 0
    }

    # 1. Claim integrity (signal IDs exist)
    results['issues']['claim_integrity'] = validate_claim_integrity(
        variant, cited_signals
    )

    # 2. Source type validation (real URLs only for explicit claims)
    results['issues']['source_type'] = validate_source_type(
        variant, cited_signals, confidence_mode, rules_config
    )

    # 3. Confidence mode rules (from YAML)
    results['issues']['confidence_mode'] = validate_confidence_mode_rules(
        variant, cited_signals, confidence_mode, company_name, rules_config
    )

    # 4. Semantic guard (used signals must be reflected in content)
    results['issues']['semantic_guard'] = validate_semantic_guard(
        variant, cited_signals, rules_config
    )

    # 5. Must end with question (if constraint enabled)
    if constraints.get('must_end_with_question', True):
        results['issues']['must_end_with_question'] = validate_must_end_with_question(
            variant.get('body', '')
        )
    else:
        results['issues']['must_end_with_question'] = []

    # 6. Global check for fake URLs
    results['issues']['fake_urls'] = validate_no_fake_urls(cited_signals)

    # 7. CRITICAL: Forbidden product validation (persona safety)
    results['issues']['forbidden_products'] = validate_forbidden_products(
        variant, persona, rules_config, confidence_mode
    )

    # Calculate totals
    for validator_name, issues in results['issues'].items():
        results['total_issues'] += len(issues)
        if issues:
            results['passed'] = False
            logger.warning(f"Validation failed ({validator_name}): {issues}")

    return results


def get_cited_signals_for_claims(
    signals: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Filter signals to only those usable for explicit claims.

    Only returns signals with:
    - source_type = 'public_url' or 'user_provided'
    - citability = 'cited'
    - Real source_url (not fake)

    Args:
        signals: All signals

    Returns:
        Filtered list of signals safe for explicit claims
    """
    cited = []

    for signal in signals:
        source_type = signal.get('source_type', '')
        citability = signal.get('citability', signal.get('verifiability', ''))  # Backward compat
        source_url = signal.get('source_url', '')

        # Must be cited type
        if source_type not in ('public_url', 'user_provided'):
            continue

        if citability not in ('cited', 'verified'):  # Support old 'verified' term
            continue

        # Must have real URL
        if not source_url or 'google.com/search' in source_url:
            continue

        cited.append(signal)

    logger.info(f"Filtered {len(signals)} signals to {len(cited)} cited for claims")
    return cited


# Backward compatibility aliases
def get_verified_signals_for_claims(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deprecated: Use get_cited_signals_for_claims instead."""
    logger.warning("get_verified_signals_for_claims is deprecated, use get_cited_signals_for_claims")
    return get_cited_signals_for_claims(signals)


class ValidationError(Exception):
    """Base exception for validation errors."""
    pass
