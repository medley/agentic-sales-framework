"""
LLM Angle Scorer - Ranks candidate angles by relevance, urgency, and reply likelihood

This module provides lightweight LLM-based scoring for angle selection.
The LLM scores pre-filtered candidate angles but does NOT:
- Invent new signals
- Introduce new angles
- Make the final selection decision

The final selection is deterministic based on weighted scores.

CLI Mode Behavior:
    In CLI mode, LLM scoring is disabled and deterministic fallback is used.
    This allows the system to run without Anthropic API keys when inside Claude Code.

Usage:
    from llm_angle_scorer import score_angles

    result = score_angles(
        persona="quality",
        company_name="Acme Corp",
        verified_signals=[...],
        candidate_angles=[...],
        scoring_weights={"relevance": 0.45, "urgency": 0.35, "reply_likelihood": 0.20}
    )
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class AngleScorerError(Exception):
    """Base exception for angle scorer errors."""
    pass


# Model configuration - override via ANTHROPIC_MODEL env var
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


def score_angles(
    persona: str,
    company_name: str,
    verified_signals: List[Dict[str, Any]],
    candidate_angles: List[Dict[str, Any]],
    scoring_weights: Dict[str, float],
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Score candidate angles using LLM for relevance, urgency, and reply likelihood.

    In CLI mode, returns deterministic fallback scores without calling the API.

    The LLM receives only:
    - Persona
    - Company name
    - Verified signals (no new facts allowed)
    - Candidate angle descriptions (no new angles allowed)

    Args:
        persona: Detected persona (quality, operations, it, regulatory)
        company_name: Company name for context
        verified_signals: List of verified signals with source_url, type, scope, recency
        candidate_angles: List of eligible angles with angle_id, name, description
        scoring_weights: Weights for relevance, urgency, reply_likelihood
        model: Model to use for scoring

    Returns:
        {
            'status': 'success' | 'error' | 'cli_fallback',
            'scores': [
                {
                    'angle_id': str,
                    'relevance': 1-5,
                    'urgency': 1-5,
                    'reply_likelihood': 1-5,
                    'weighted_score': float,
                    'reason': str
                }
            ],
            'error': str (if status='error'),
            'cli_mode': bool
        }
    """
    # Import execution mode here to avoid circular imports
    # Use try/except to handle both package and direct imports
    try:
        from .execution_mode import is_cli_mode, WARNING_LLM_API_DISABLED_CLI_MODE
    except ImportError:
        from execution_mode import is_cli_mode, WARNING_LLM_API_DISABLED_CLI_MODE

    logger.info(f"Scoring {len(candidate_angles)} angles for {company_name} ({persona})")

    # Validation
    if not persona:
        return {
            'status': 'error',
            'scores': [],
            'error': 'Persona is required for angle scoring',
            'cli_mode': is_cli_mode()
        }

    if not company_name or company_name == 'Unknown Company':
        return {
            'status': 'error',
            'scores': [],
            'error': 'Valid company name is required for angle scoring',
            'cli_mode': is_cli_mode()
        }

    if not candidate_angles:
        return {
            'status': 'error',
            'scores': [],
            'error': 'No candidate angles provided',
            'cli_mode': is_cli_mode()
        }

    if len(candidate_angles) > 10:
        logger.warning(f"Too many candidates ({len(candidate_angles)}), limiting to 10")
        candidate_angles = candidate_angles[:10]

    # CLI MODE: Return deterministic fallback scores
    if is_cli_mode():
        logger.info("CLI mode detected - using deterministic fallback scoring")
        return _score_angles_deterministic(
            candidate_angles=candidate_angles,
            scoring_weights=scoring_weights,
            warning=WARNING_LLM_API_DISABLED_CLI_MODE
        )

    # Build prompt
    prompt = _build_scoring_prompt(
        persona=persona,
        company_name=company_name,
        verified_signals=verified_signals,
        candidate_angles=candidate_angles
    )

    # Call LLM
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            # In headless mode, missing API key is an error
            raise AngleScorerError("ANTHROPIC_API_KEY not set")

        # Import Anthropic only when needed (not in CLI mode)
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        response = client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0.0,  # Deterministic scoring
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        raw_output = response.content[0].text
        logger.debug(f"LLM raw output: {raw_output}")

        scores = _parse_scoring_output(raw_output, candidate_angles)

        # Calculate weighted scores
        for score in scores:
            score['weighted_score'] = (
                score['relevance'] * scoring_weights.get('relevance', 0.45) +
                score['urgency'] * scoring_weights.get('urgency', 0.35) +
                score['reply_likelihood'] * scoring_weights.get('reply_likelihood', 0.20)
            )

        logger.info(f"Successfully scored {len(scores)} angles")

        return {
            'status': 'success',
            'scores': scores,
            'raw_output': raw_output
        }

    except Exception as e:
        logger.error(f"Angle scoring failed: {e}", exc_info=True)
        return {
            'status': 'error',
            'scores': [],
            'error': str(e)
        }


def _build_scoring_prompt(
    persona: str,
    company_name: str,
    verified_signals: List[Dict[str, Any]],
    candidate_angles: List[Dict[str, Any]]
) -> str:
    """
    Build LLM prompt for angle scoring.

    Hard constraints:
    - LLM cannot introduce new signals
    - LLM cannot introduce new angles
    - Reasons must only reference existing verified_signals
    """
    # Format verified signals
    signals_text = []
    for i, signal in enumerate(verified_signals, 1):
        signals_text.append(
            f"{i}. [{signal['signal_type']}] {signal['claim']}\n"
            f"   Source: {signal['source_url']}\n"
            f"   Scope: {signal['scope']} | Recency: {signal['recency_days']} days ago"
        )

    signals_section = "\n".join(signals_text) if signals_text else "No verified signals available"

    # Format candidate angles
    angles_text = []
    for angle in candidate_angles:
        angles_text.append(
            f"- angle_id: \"{angle['angle_id']}\"\n"
            f"  name: \"{angle['name']}\"\n"
            f"  description: \"{angle['description']}\""
        )

    angles_section = "\n".join(angles_text)

    prompt = f"""You are scoring messaging angles for a B2B sales email to a {persona} at {company_name}.

VERIFIED SIGNALS (you must ONLY reference these, no new facts):
{signals_section}

CANDIDATE ANGLES (you must score ONLY these, no new angles):
{angles_section}

SCORING RUBRIC:
For each candidate angle, score on 1-5 scale:

1. Relevance (1-5):
   - How well do the verified signals match this angle?
   - 5 = Perfect match (multiple signals directly support this angle)
   - 3 = Moderate match (some signals relate)
   - 1 = Weak match (signals barely relate)

2. Urgency (1-5):
   - Based on signal recency and type, how time-sensitive is this pain?
   - 5 = Urgent (recent regulatory event, leadership change)
   - 3 = Moderate urgency (older signals, slower-moving issues)
   - 1 = Low urgency (general industry trends)

3. Reply Likelihood (1-5):
   - How likely is a {persona} to respond to this angle?
   - 5 = Highly likely (direct pain point for this persona)
   - 3 = Moderately likely (relevant but not primary concern)
   - 1 = Unlikely (not their main responsibility)

RULES:
- You must score EVERY candidate angle
- Your "reason" must be ONE sentence and reference ONLY the verified signals above
- Do NOT invent new signals or facts
- Do NOT introduce new angles
- Do NOT make the final selection (that's done deterministically)

OUTPUT FORMAT (strict JSON):
{{
  "scores": [
    {{
      "angle_id": "regulatory_pressure",
      "relevance": 4,
      "urgency": 5,
      "reply_likelihood": 4,
      "reason": "Recent regulatory event signal strongly supports audit readiness focus"
    }},
    ...
  ]
}}

Return ONLY the JSON, no other text."""

    return prompt


def _parse_scoring_output(
    raw_output: str,
    candidate_angles: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Parse LLM output and validate against candidate angles.

    Hard rules:
    - Must be valid JSON
    - Must have 'scores' array
    - Each score must have angle_id matching a candidate
    - Missing or invalid angle_ids are dropped (not errors)

    Returns:
        List of valid score dicts
    """
    try:
        # Extract JSON from output (handle markdown code blocks)
        json_text = raw_output.strip()

        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0].strip()

        data = json.loads(json_text)

        if 'scores' not in data:
            raise ValueError("Missing 'scores' key in output")

        raw_scores = data['scores']

        # Validate scores
        valid_scores = []
        valid_angle_ids = {a['angle_id'] for a in candidate_angles}

        for score in raw_scores:
            angle_id = score.get('angle_id')

            # Check angle_id is valid
            if angle_id not in valid_angle_ids:
                logger.warning(f"Dropping invalid angle_id: {angle_id}")
                continue

            # Check required fields
            if not all(k in score for k in ['relevance', 'urgency', 'reply_likelihood']):
                logger.warning(f"Dropping score with missing fields: {angle_id}")
                continue

            # Validate score ranges (1-5)
            try:
                relevance = int(score['relevance'])
                urgency = int(score['urgency'])
                reply_likelihood = int(score['reply_likelihood'])

                if not all(1 <= s <= 5 for s in [relevance, urgency, reply_likelihood]):
                    logger.warning(f"Dropping score with out-of-range values: {angle_id}")
                    continue

                valid_scores.append({
                    'angle_id': angle_id,
                    'relevance': relevance,
                    'urgency': urgency,
                    'reply_likelihood': reply_likelihood,
                    'reason': score.get('reason', 'No reason provided')[:200]  # Limit length
                })

            except (ValueError, TypeError) as e:
                logger.warning(f"Dropping score with invalid numeric values: {angle_id} - {e}")
                continue

        if not valid_scores:
            raise ValueError("No valid scores parsed from output")

        logger.info(f"Parsed {len(valid_scores)} valid scores from {len(raw_scores)} raw scores")

        return valid_scores

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from LLM output: {e}")
        raise AngleScorerError(f"Invalid JSON output: {e}")

    except Exception as e:
        logger.error(f"Failed to parse scoring output: {e}")
        raise AngleScorerError(f"Parsing error: {e}")


def select_best_angle(
    scored_angles: List[Dict[str, Any]],
    deterministic_priorities: Dict[str, int]
) -> Dict[str, Any]:
    """
    Deterministically select best angle from scored angles.

    Uses weighted_score as primary criterion, deterministic priority for tie-breaking.

    Args:
        scored_angles: List of angles with weighted_score
        deterministic_priorities: Dict of angle_id -> priority (higher = better)

    Returns:
        {
            'chosen_angle_id': str,
            'chosen_angle_reason': str,
            'weighted_score': float,
            'tie_break_used': bool
        }
    """
    if not scored_angles:
        raise ValueError("No scored angles to select from")

    # Sort by weighted_score (descending), then by deterministic priority (descending)
    sorted_angles = sorted(
        scored_angles,
        key=lambda a: (
            a['weighted_score'],
            deterministic_priorities.get(a['angle_id'], 0)
        ),
        reverse=True
    )

    best = sorted_angles[0]

    # Check if tie-break was needed
    tie_break_used = False
    if len(sorted_angles) > 1:
        second = sorted_angles[1]
        if abs(best['weighted_score'] - second['weighted_score']) < 0.01:
            tie_break_used = True
            logger.info(
                f"Tie-break used: {best['angle_id']} vs {second['angle_id']} "
                f"(both ~{best['weighted_score']:.2f})"
            )

    return {
        'chosen_angle_id': best['angle_id'],
        'chosen_angle_reason': best['reason'],
        'weighted_score': best['weighted_score'],
        'tie_break_used': tie_break_used
    }


def _score_angles_deterministic(
    candidate_angles: List[Dict[str, Any]],
    scoring_weights: Dict[str, float],
    warning: str
) -> Dict[str, Any]:
    """
    Generate deterministic fallback scores for CLI mode.

    Uses a simple heuristic based on angle priority/position in the list.
    First angle gets highest scores, decreasing from there.

    Args:
        candidate_angles: List of eligible angles with angle_id, name, description
        scoring_weights: Weights for relevance, urgency, reply_likelihood
        warning: Warning message to include in result

    Returns:
        Same format as score_angles() with status='cli_fallback'
    """
    scores = []

    for i, angle in enumerate(candidate_angles):
        # Assign decreasing scores based on position (first = best)
        # This respects the deterministic priority order from the rules
        base_score = max(5 - i, 1)

        relevance = base_score
        urgency = max(base_score - 1, 1)  # Slightly lower urgency
        reply_likelihood = base_score

        weighted_score = (
            relevance * scoring_weights.get('relevance', 0.45) +
            urgency * scoring_weights.get('urgency', 0.35) +
            reply_likelihood * scoring_weights.get('reply_likelihood', 0.20)
        )

        scores.append({
            'angle_id': angle['angle_id'],
            'relevance': relevance,
            'urgency': urgency,
            'reply_likelihood': reply_likelihood,
            'weighted_score': weighted_score,
            'reason': f"Deterministic fallback (CLI mode) - angle priority {i + 1}"
        })

    logger.info(f"Generated deterministic scores for {len(scores)} angles")

    return {
        'status': 'cli_fallback',
        'scores': scores,
        'cli_mode': True,
        'warning': warning
    }
