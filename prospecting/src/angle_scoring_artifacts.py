"""
Angle Scoring Artifacts - Write scoring results to deliverables

Writes angle_scoring.json with:
- Candidate angles
- Raw LLM scores (if used)
- Weighted totals
- Chosen angle_id
- Tie-break info
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def write_angle_scoring_artifact(
    prospect_brief: Dict[str, Any],
    output_dir: Optional[Path] = None
) -> Optional[Path]:
    """
    Write angle scoring metadata to angle_scoring.json.

    Args:
        prospect_brief: Prospect brief with angle_scoring_metadata
        output_dir: Directory to write to (defaults to deliverables/)

    Returns:
        Path to written file, or None if no scoring metadata
    """
    angle_scoring_metadata = prospect_brief.get('angle_scoring_metadata')

    if not angle_scoring_metadata:
        logger.info("No angle scoring metadata to write")
        return None

    # Default output directory
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'deliverables'

    output_dir.mkdir(parents=True, exist_ok=True)

    # Build artifact
    artifact = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'company_name': prospect_brief.get('company_name', 'Unknown'),
        'persona': prospect_brief.get('persona', 'Unknown'),
        'industry': prospect_brief.get('industry', 'Unknown'),
        'method': angle_scoring_metadata.get('method', 'unknown'),
        'chosen_angle_id': prospect_brief.get('angle_id'),
        'candidate_angles': angle_scoring_metadata.get('candidate_angles', [])
    }

    # Add path information
    fallback_reason = angle_scoring_metadata.get('fallback_reason')
    num_candidates = len(angle_scoring_metadata.get('candidate_angles', []))

    if angle_scoring_metadata['method'] == 'deterministic':
        if num_candidates == 1:
            artifact['path'] = 'only_1_candidate_skipped_llm'
        elif fallback_reason:
            artifact['path'] = 'llm_failed_fallback'
            artifact['fallback_reason'] = fallback_reason
        else:
            artifact['path'] = 'llm_disabled_in_config'
    elif angle_scoring_metadata['method'] == 'llm_scored':
        artifact['path'] = 'llm_scoring_used'

    # Add method-specific fields
    if angle_scoring_metadata['method'] == 'llm_scored':
        artifact.update({
            'angle_scores': angle_scoring_metadata.get('angle_scores', []),
            'chosen_reason': angle_scoring_metadata.get('chosen_reason', ''),
            'weighted_score': angle_scoring_metadata.get('weighted_score', 0.0),
            'tie_break_used': angle_scoring_metadata.get('tie_break_used', False),
            'scoring_weights': angle_scoring_metadata.get('scoring_weights', {})
        })
    elif angle_scoring_metadata['method'] == 'deterministic':
        artifact.update({
            'deterministic_scores': angle_scoring_metadata.get('deterministic_scores', {})
        })

    # Write to file
    output_path = output_dir / 'angle_scoring.json'

    try:
        with open(output_path, 'w') as f:
            json.dump(artifact, f, indent=2)

        logger.info(f"Wrote angle scoring artifact to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to write angle scoring artifact: {e}")
        return None


def format_angle_scoring_summary(prospect_brief: Dict[str, Any]) -> str:
    """
    Format angle scoring summary for display.

    Args:
        prospect_brief: Prospect brief with angle_scoring_metadata

    Returns:
        Formatted summary string
    """
    angle_scoring_metadata = prospect_brief.get('angle_scoring_metadata')

    if not angle_scoring_metadata:
        return "Angle Selection: Not available"

    method = angle_scoring_metadata.get('method', 'unknown')
    chosen_angle = prospect_brief.get('angle_id', 'None')
    candidates = angle_scoring_metadata.get('candidate_angles', [])
    fallback_reason = angle_scoring_metadata.get('fallback_reason', None)

    lines = [
        "\n--- Angle Selection ---",
        f"Method: {method.upper()}",
        f"Candidates considered: {len(candidates)}",
        f"  {', '.join(candidates)}",
        f"Chosen angle: {chosen_angle}"
    ]

    # Add path indicator to show why this method was used
    if method == 'deterministic':
        if len(candidates) == 1:
            lines.append("\nPath: Only 1 candidate → skipped LLM")
        elif fallback_reason:
            lines.append(f"\nPath: LLM failed → fallback to deterministic")
            lines.append(f"  Reason: {fallback_reason}")
        else:
            lines.append("\nPath: LLM scoring disabled in config")
    elif method == 'llm_scored':
        lines.append("\nPath: 2+ candidates → LLM scoring used")

    if method == 'llm_scored':
        scores = angle_scoring_metadata.get('angle_scores', [])
        weighted_score = angle_scoring_metadata.get('weighted_score', 0.0)
        tie_break = angle_scoring_metadata.get('tie_break_used', False)
        reason = angle_scoring_metadata.get('chosen_reason', '')

        lines.append(f"\nWeighted score: {weighted_score:.2f}")

        if tie_break:
            lines.append("Tie-break: YES (used deterministic priority)")

        lines.append(f"\nReason: {reason}")

        lines.append("\nAll scores:")
        for score in scores:
            lines.append(
                f"  {score['angle_id']}: "
                f"R={score['relevance']} U={score['urgency']} "
                f"RL={score['reply_likelihood']} "
                f"→ {score.get('weighted_score', 0.0):.2f}"
            )

    elif method == 'deterministic':
        det_scores = angle_scoring_metadata.get('deterministic_scores', {})
        lines.append("\nDeterministic scores:")
        for angle_id, score in det_scores.items():
            marker = "✓" if angle_id == chosen_angle else " "
            lines.append(f"  {marker} {angle_id}: {score}")

    return '\n'.join(lines)
