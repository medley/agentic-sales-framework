"""
Cadence Generator - Generate multi-step outbound sequences

This module generates sequence files from email_context.json without
re-running strategy selection. All steps inherit from the initial context.

Core Principle:
    Strategy is decided once. Rendering can happen many times.
    No new research, no new angle selection, no new scoring.

Usage:
    from cadence.cadence_generator import generate_sequence

    result = generate_sequence(
        context=email_context,
        cadence_name='standard_12day',
        rules_config=rules_config
    )
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from .cadence_registry import (
    get_cadence,
    get_cadence_steps,
    validate_cadence_name,
    get_cadence_duration_days,
)

logger = logging.getLogger(__name__)


# =============================================================================
# STEP RESULT DATA STRUCTURE
# =============================================================================

class StepResult:
    """Result of rendering a single cadence step."""

    def __init__(
        self,
        step_number: int,
        day: int,
        channel: str,
        step_type: str,
        status: str = 'PENDING',
        copy: str = '',
        subject: Optional[str] = None,
        constraints_applied: Optional[Dict] = None,
        validation: Optional[Dict] = None,
        repairs_applied: Optional[List[str]] = None,
        error: Optional[str] = None,
        optional: bool = False,
    ):
        self.step_number = step_number
        self.day = day
        self.channel = channel
        self.step_type = step_type
        self.status = status  # PASSED, FAILED, SKIPPED, PENDING
        self.copy = copy
        self.subject = subject
        self.constraints_applied = constraints_applied or {}
        self.validation = validation or {}
        self.repairs_applied = repairs_applied or []
        self.error = error
        self.optional = optional

    def to_dict(self) -> Dict[str, Any]:
        return {
            'step': self.step_number,
            'day': self.day,
            'channel': self.channel,
            'step_type': self.step_type,
            'status': self.status,
            'copy': self.copy,
            'subject': self.subject,
            'constraints_applied': self.constraints_applied,
            'validation': self.validation,
            'repairs_applied': self.repairs_applied,
            'error': self.error,
            'optional': self.optional,
        }


# =============================================================================
# CADENCE GENERATOR CLASS
# =============================================================================

class CadenceGenerator:
    """
    Generate multi-step outbound sequences from email_context.json.

    All steps inherit strategy from the initial context:
    - persona
    - product eligibility
    - confidence_mode
    - angle_id
    - offer_id

    No new claims after step 1.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        rules_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize generator with email context.

        Args:
            context: email_context.json contents
            rules_config: Rules configuration (for validation)
        """
        self.context = context
        self.rules_config = rules_config or {}

        # Extract inherited strategy
        prospect_brief = context.get('prospect_brief', {})
        self.persona = prospect_brief.get('persona')
        self.confidence_mode = prospect_brief.get('confidence_tier', 'generic')
        self.angle_id = prospect_brief.get('angle_id')
        self.offer_id = prospect_brief.get('offer_id')
        self.verified_signals = prospect_brief.get('verified_signals', [])
        self.base_constraints = prospect_brief.get('constraints', {})

        # Contact info
        contact = context.get('contact', {})
        self.first_name = contact.get('first_name', 'there')
        self.company_name = prospect_brief.get('company_name', '')

        # Email plan for step 1
        self.email_plan = context.get('email_plan', {})

        # Store rendered step 1 for reference in later steps
        self.step_1_copy: Optional[str] = None
        self.step_1_subject: Optional[str] = None

    def generate(
        self,
        cadence_name: str,
        include_optional: bool = False,
        step_1_rendered: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate full cadence sequence.

        Args:
            cadence_name: Name of cadence template
            include_optional: Whether to include optional steps
            step_1_rendered: Pre-rendered step 1 (if available)

        Returns:
            Sequence result dict with metadata and step results
        """
        if not validate_cadence_name(cadence_name):
            return {
                'status': 'error',
                'error': f"Unknown cadence: {cadence_name}",
                'cadence_name': cadence_name,
                'steps': [],
            }

        cadence = get_cadence(cadence_name)
        steps = get_cadence_steps(cadence_name, include_optional=include_optional)

        # Store step 1 if provided
        if step_1_rendered:
            self.step_1_copy = step_1_rendered.get('body', '')
            self.step_1_subject = step_1_rendered.get('subject', '')

        # Generate each step
        step_results = []
        for step_def in steps:
            result = self._render_step(step_def)
            step_results.append(result)

            # Store step 1 output for reference in later steps
            if step_def.get('step') == 1 and result.status == 'PASSED':
                self.step_1_copy = result.copy
                self.step_1_subject = result.subject

        # Calculate overall status
        required_steps = [r for r in step_results if not r.optional]
        passed_required = sum(1 for r in required_steps if r.status == 'PASSED')
        failed_required = sum(1 for r in required_steps if r.status == 'FAILED')

        if failed_required == len(required_steps):
            overall_status = 'all_failed'
        elif failed_required > 0:
            overall_status = 'partial'
        else:
            overall_status = 'success'

        return {
            'status': overall_status,
            'cadence_name': cadence_name,
            'cadence_display_name': cadence.get('name', cadence_name),
            'cadence_duration_days': get_cadence_duration_days(cadence_name),
            'generated_at': datetime.now().isoformat(),
            'inherited_strategy': {
                'persona': self.persona,
                'confidence_mode': self.confidence_mode,
                'angle_id': self.angle_id,
                'offer_id': self.offer_id,
            },
            'contact': {
                'first_name': self.first_name,
                'company_name': self.company_name,
            },
            'step_summary': {
                'total': len(step_results),
                'required': len(required_steps),
                'passed': sum(1 for r in step_results if r.status == 'PASSED'),
                'failed': sum(1 for r in step_results if r.status == 'FAILED'),
                'skipped': sum(1 for r in step_results if r.status == 'SKIPPED'),
            },
            'steps': [r.to_dict() for r in step_results],
        }

    def _render_step(self, step_def: Dict[str, Any]) -> StepResult:
        """
        Render a single step.

        Args:
            step_def: Step definition from cadence

        Returns:
            StepResult with rendered copy or error
        """
        step_number = step_def.get('step', 0)
        day = step_def.get('day', 1)
        channel = step_def.get('channel', 'email')
        step_type = step_def.get('step_type', 'initial')
        optional = step_def.get('optional', False)

        result = StepResult(
            step_number=step_number,
            day=day,
            channel=channel,
            step_type=step_type,
            optional=optional,
        )

        try:
            # Get constraints for this step
            from channel_constraints import get_step_constraints
            constraints = get_step_constraints(
                channel=channel,
                step_type=step_type,
                base_constraints=self.base_constraints,
            )
            result.constraints_applied = constraints

            # Render step content
            if step_number == 1:
                # Step 1: Use email_plan from context
                copy, subject = self._render_initial_step(channel)
            else:
                # Later steps: Use template or generate from context
                copy, subject = self._render_follow_up_step(step_def)

            result.copy = copy
            result.subject = subject

            # Validate step
            validation_result = self._validate_step(copy, subject, constraints, step_type)
            result.validation = validation_result

            if validation_result.get('passed', False):
                result.status = 'PASSED'
            else:
                # Attempt repair
                repaired_copy, repaired_subject, repairs = self._repair_step(
                    copy, subject, validation_result.get('failures', []), constraints
                )
                result.repairs_applied = repairs

                # Re-validate
                validation_result = self._validate_step(repaired_copy, repaired_subject, constraints, step_type)
                result.validation = validation_result

                if validation_result.get('passed', False):
                    result.copy = repaired_copy
                    result.subject = repaired_subject
                    result.status = 'PASSED'
                else:
                    result.status = 'FAILED'
                    result.error = f"Validation failed: {validation_result.get('failures', [])}"

        except Exception as e:
            result.status = 'FAILED'
            result.error = str(e)
            logger.exception(f"Error rendering step {step_number}: {e}")

        return result

    def _render_initial_step(self, channel: str) -> Tuple[str, Optional[str]]:
        """
        Render step 1 from email_plan in context.

        Args:
            channel: Output channel (email, inmail, voicemail)

        Returns:
            Tuple of (copy, subject)
        """
        # Get draft sentences
        sentences = []
        for i in range(1, 5):
            sent = self.email_plan.get(f'sentence_{i}_draft', '')
            if sent:
                sentences.append(sent)

        if not sentences:
            raise ValueError("No draft sentences found in email_plan")

        # Get subject
        subject_candidates = self.email_plan.get('subject_candidates', ['quick question'])
        subject = subject_candidates[0] if subject_candidates else 'quick question'

        # Format based on channel
        if channel == 'email':
            greeting = f"{self.first_name},"
            body = '\n\n'.join(sentences)
            closing = "\n\n[Your Name]"
            copy = f"{greeting}\n\n{body}{closing}"

        elif channel == 'inmail':
            greeting = f"Hi {self.first_name},"
            # Convert to paragraph format for InMail
            if len(sentences) >= 2:
                para1 = sentences[0]
                para2 = ' '.join(sentences[1:])
                copy = f"{greeting}\n\n{para1}\n\n{para2}\n\n{{sender_name}}"
            else:
                copy = f"{greeting}\n\n{sentences[0]}\n\n{{sender_name}}"
            subject = None  # InMail doesn't use subject

        elif channel == 'voicemail':
            # Use voicemail template
            angle_hook = sentences[0] if sentences else "Thought it was worth reaching out."
            copy = (
                f"Hey {self.first_name}, this is {{sender_name}} with {{company_name}}.\n"
                f"{angle_hook}\n"
                "Thought it was worth a quick call.\n"
                "My number is [callback]. Looking forward to connecting."
            )
            subject = None

        else:
            # Fallback to email format
            greeting = f"{self.first_name},"
            body = '\n\n'.join(sentences)
            closing = "\n\n{sender_name}"
            copy = f"{greeting}\n\n{body}{closing}"

        return copy, subject

    def _render_follow_up_step(self, step_def: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """
        Render a follow-up step (step 2+).

        Uses templates or generates from context.
        No new claims allowed.

        Args:
            step_def: Step definition

        Returns:
            Tuple of (copy, subject)
        """
        step_type = step_def.get('step_type', 'bump')
        channel = step_def.get('channel', 'email')
        template = step_def.get('template')

        # Get angle info for template substitution
        angle_question = self._get_angle_question()
        angle_topic = self._get_angle_topic()

        if template:
            # Use step template
            copy = template.format(
                first_name=self.first_name,
                angle_question=angle_question,
                angle_topic=angle_topic,
                company_name=self.company_name,
            )
        else:
            # Generate based on step type
            copy = self._generate_follow_up_copy(step_type, channel)

        # Add greeting for emails
        if channel == 'email' and not copy.startswith(self.first_name):
            copy = f"{self.first_name},\n\n{copy}\n\n[Your Name]"
        elif channel == 'inmail' and not copy.startswith('Hi'):
            copy = f"Hi {self.first_name},\n\n{copy}\n\n[Your Name]"

        # Subject for follow-ups is typically None (reply thread)
        subject = None

        return copy, subject

    def _generate_follow_up_copy(self, step_type: str, channel: str) -> str:
        """
        Generate follow-up copy based on step type.

        Args:
            step_type: Type of step (bump, reframe, breakup, etc.)
            channel: Output channel

        Returns:
            Generated copy
        """
        angle_question = self._get_angle_question()
        angle_topic = self._get_angle_topic()

        if step_type == 'bump':
            return f"Just floating this back up - {angle_question}"

        elif step_type == 'gentle_bump':
            return (
                f"Wanted to check back on this. "
                f"Still curious if {angle_topic.lower()} is something you're thinking about?"
            )

        elif step_type == 'reframe':
            return (
                f"Different angle on this - even if {angle_topic.lower()} isn't top of mind, "
                f"the checklist might spark something useful. Want me to send it over?"
            )

        elif step_type == 'breakup':
            return (
                f"Not trying to fill your inbox. "
                f"If {angle_topic.lower()} isn't a priority right now, no worries at all."
            )

        elif step_type == 'follow_on':
            return (
                f"Sent you a note on LinkedIn earlier this week about {angle_topic.lower()}. "
                f"Thought I'd follow up here in case that's easier. {angle_question}"
            )

        else:
            return f"Following up on my previous note. {angle_question}"

    def _get_angle_question(self) -> str:
        """Get the angle question from context or generate one."""
        # Try to extract from email_plan offer
        offer_text = self.email_plan.get('sentence_3_draft', '')
        if offer_text and '?' in offer_text:
            return offer_text.split('?')[0] + '?'

        # Fallback based on angle
        angle_questions = {
            'capa_cycle_time': 'is CAPA cycle time something you\'re trying to improve?',
            'batch_release_time': 'is batch release time on your radar?',
            'validation_governance': 'are you looking to simplify validation governance?',
            'audit_readiness': 'is audit readiness a priority right now?',
            'equipment_reliability': 'is equipment reliability something you\'re focused on?',
            'digital_transformation': 'are you exploring digital transformation initiatives?',
        }

        return angle_questions.get(self.angle_id, 'is this something you\'re thinking about?')

    def _get_angle_topic(self) -> str:
        """Get the angle topic name."""
        angle_topics = {
            'capa_cycle_time': 'CAPA cycle time',
            'batch_release_time': 'batch release time',
            'validation_governance': 'validation governance',
            'audit_readiness': 'audit readiness',
            'equipment_reliability': 'equipment reliability',
            'digital_transformation': 'digital transformation',
            'training_compliance': 'training compliance',
            'review_by_exception': 'review by exception',
            'production_visibility': 'production visibility',
            'calibration_compliance': 'calibration compliance',
            'data_integrity': 'data integrity',
            'operational_efficiency': 'operational efficiency',
        }

        return angle_topics.get(self.angle_id, 'this topic')

    def _validate_step(
        self,
        copy: str,
        subject: Optional[str],
        constraints: Dict[str, Any],
        step_type: str
    ) -> Dict[str, Any]:
        """
        Validate a step's copy against constraints.

        Args:
            copy: Step copy
            subject: Subject line (if applicable)
            constraints: Merged constraints for this step
            step_type: Type of step

        Returns:
            Validation result dict
        """
        failures = []

        # Word count
        word_count = len(copy.split())
        word_min = constraints.get('word_count_min', 0)
        word_max = constraints.get('word_count_max', 999)

        if word_count < word_min:
            failures.append(f"word_count_low:{word_count}:{word_min}")
        elif word_count > word_max:
            failures.append(f"word_count_high:{word_count}:{word_max}")

        # Question ending (if required)
        if constraints.get('must_end_with_question', False):
            # Check body ends with ?
            body = copy.strip()
            # Remove signature
            lines = body.split('\n')
            while lines and len(lines[-1].strip()) < 20 and lines[-1].strip().isalpha():
                lines.pop()
            body = '\n'.join(lines).strip()

            if not body.endswith('?'):
                failures.append('no_question_ending')

        # Subject validation (if required)
        if constraints.get('subject_required', False):
            if not subject:
                failures.append('missing_subject')
            else:
                subject_words = len(subject.split())
                subject_max = constraints.get('subject_word_max', 4)
                if subject_words > subject_max:
                    failures.append(f"subject_too_long:{subject_words}:{subject_max}")

        # Product pitch check
        pitch_terms = ['product_name', 'qx', 'mx', 'our platform', 'our solution',
                       'our software', 'we offer', 'we provide']
        found_pitch = [t for t in pitch_terms if t.lower() in copy.lower()]
        if found_pitch:
            failures.append(f"product_pitch:{','.join(found_pitch)}")

        # Forbidden products check (uses validators module)
        try:
            from validators import validate_forbidden_products
            variant = {'body': copy, 'subject': subject or ''}
            forbidden_issues = validate_forbidden_products(
                variant, self.persona, self.rules_config, self.confidence_mode
            )
            for issue in forbidden_issues:
                failures.append(f"forbidden_product:{issue}")
        except ImportError:
            pass  # Validators not available, skip

        return {
            'passed': len(failures) == 0,
            'failures': failures,
            'word_count': word_count,
        }

    def _repair_step(
        self,
        copy: str,
        subject: Optional[str],
        failures: List[str],
        constraints: Dict[str, Any]
    ) -> Tuple[str, Optional[str], List[str]]:
        """
        Attempt to repair validation failures.

        Args:
            copy: Original copy
            subject: Original subject
            failures: List of failure codes
            constraints: Constraints for this step

        Returns:
            Tuple of (repaired_copy, repaired_subject, repairs_applied)
        """
        repairs_applied = []
        repaired_copy = copy
        repaired_subject = subject

        for failure in failures:
            if failure == 'no_question_ending':
                # Convert last sentence to question
                repaired_copy = repaired_copy.rstrip('.!')
                if not repaired_copy.endswith('?'):
                    repaired_copy += '?'
                repairs_applied.append('converted_to_question')

            elif failure.startswith('word_count_high:'):
                # Trim words
                word_max = constraints.get('word_count_max', 100)
                words = repaired_copy.split()
                if len(words) > word_max:
                    repaired_copy = ' '.join(words[:word_max])
                    repairs_applied.append('trimmed_words')

            elif failure.startswith('subject_too_long:'):
                # Truncate subject
                if repaired_subject:
                    subject_max = constraints.get('subject_word_max', 4)
                    words = repaired_subject.split()
                    if len(words) > subject_max:
                        repaired_subject = ' '.join(words[:subject_max])
                        repairs_applied.append('truncated_subject')

        return repaired_copy, repaired_subject, repairs_applied


# =============================================================================
# SEQUENCE FILE GENERATION
# =============================================================================

def format_sequence_markdown(result: Dict[str, Any]) -> str:
    """
    Format sequence result as readable Markdown.

    Args:
        result: Sequence result from CadenceGenerator.generate()

    Returns:
        Formatted Markdown string
    """
    lines = []

    # Header
    lines.append(f"# {result.get('cadence_display_name', 'Outbound Sequence')}")
    lines.append("")
    lines.append(f"**Generated:** {result.get('generated_at', 'Unknown')}")
    lines.append(f"**Status:** {result.get('status', 'Unknown')}")
    lines.append(f"**Duration:** {result.get('cadence_duration_days', 0)} days")
    lines.append("")

    # Inherited strategy
    strategy = result.get('inherited_strategy', {})
    lines.append("## Inherited Strategy")
    lines.append("")
    lines.append(f"- **Persona:** {strategy.get('persona', 'Unknown')}")
    lines.append(f"- **Confidence Mode:** {strategy.get('confidence_mode', 'Unknown')}")
    lines.append(f"- **Angle:** {strategy.get('angle_id', 'Unknown')}")
    lines.append(f"- **Offer:** {strategy.get('offer_id', 'Unknown')}")
    lines.append("")

    # Contact
    contact = result.get('contact', {})
    lines.append("## Contact")
    lines.append("")
    lines.append(f"- **First Name:** {contact.get('first_name', 'Unknown')}")
    lines.append(f"- **Company:** {contact.get('company_name', 'Unknown')}")
    lines.append("")

    # Summary
    summary = result.get('step_summary', {})
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Steps:** {summary.get('total', 0)}")
    lines.append(f"- **Required Steps:** {summary.get('required', 0)}")
    lines.append(f"- **Passed:** {summary.get('passed', 0)}")
    lines.append(f"- **Failed:** {summary.get('failed', 0)}")
    lines.append("")

    # Steps
    lines.append("## Steps")
    lines.append("")

    for step in result.get('steps', []):
        step_num = step.get('step', 0)
        day = step.get('day', 0)
        channel = step.get('channel', 'unknown')
        step_type = step.get('step_type', 'unknown')
        status = step.get('status', 'UNKNOWN')
        optional = " (optional)" if step.get('optional') else ""

        lines.append(f"### Step {step_num} | Day {day} | {channel.upper()}{optional}")
        lines.append("")
        lines.append(f"**Type:** {step_type}")
        lines.append(f"**Status:** {status}")
        lines.append("")

        if step.get('copy'):
            lines.append("**Copy:**")
            lines.append("```")
            lines.append(step['copy'])
            lines.append("```")
            lines.append("")

        if step.get('subject'):
            lines.append(f"**Subject:** {step['subject']}")
            lines.append("")

        if step.get('error'):
            lines.append(f"**Error:** {step['error']}")
            lines.append("")

        if step.get('repairs_applied'):
            lines.append(f"**Repairs Applied:** {', '.join(step['repairs_applied'])}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Footer
    lines.append("")
    lines.append("*This sequence was auto-generated and is NOT auto-sent.*")
    lines.append("*Review all copy before using in outreach.*")

    return '\n'.join(lines)


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def generate_sequence(
    context: Dict[str, Any],
    cadence_name: str,
    rules_config: Optional[Dict[str, Any]] = None,
    include_optional: bool = False,
    step_1_rendered: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a cadence sequence from email context.

    Args:
        context: email_context.json contents
        cadence_name: Name of cadence template
        rules_config: Rules configuration
        include_optional: Whether to include optional steps
        step_1_rendered: Pre-rendered step 1 (if available)

    Returns:
        Sequence result dict
    """
    generator = CadenceGenerator(context, rules_config)
    return generator.generate(
        cadence_name=cadence_name,
        include_optional=include_optional,
        step_1_rendered=step_1_rendered,
    )


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python cadence_generator.py <context_path> <cadence_name> [--include-optional]")
        print("")
        print("Example:")
        print("  python cadence_generator.py .tmp/email_context.json standard_12day")
        sys.exit(1)

    context_path = sys.argv[1]
    cadence_name = sys.argv[2]
    include_optional = '--include-optional' in sys.argv

    # Load context
    try:
        with open(context_path, 'r') as f:
            context = json.load(f)
    except Exception as e:
        print(f"Error loading context: {e}")
        sys.exit(1)

    # Generate sequence
    result = generate_sequence(
        context=context,
        cadence_name=cadence_name,
        include_optional=include_optional,
    )

    # Output
    if '--json' in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(format_sequence_markdown(result))
