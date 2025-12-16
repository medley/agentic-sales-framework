"""
Email Component Library - Structured components for intelligent email generation

Provides tagged libraries of:
- Pain points (by persona + industry)
- Regulatory triggers (by industry + date)
- CTAs with deliverables (by persona)
- Subject lines (by pain area)

Components are selected based on research data, not templates.

Usage:
    from email_components import EmailComponentLibrary

    library = EmailComponentLibrary()
    pains = library.get_pains(persona="quality", industry="medical_device")
    cta = library.get_cta(persona="quality", pain_area="audit_readiness")
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EmailComponentLibrary:
    """
    Structured library of email components with intelligent matching.

    IMPORTANT: These patterns should stay in sync with base_config.yaml.
    The YAML is the source of truth; this is a fallback for legacy code paths.
    """

    # Persona detection patterns
    # SYNC WITH: src/rules/base_config.yaml -> personas
    PERSONA_PATTERNS = {
        "quality": [
            "vp quality", "vice president quality", "head of quality",
            "director quality", "quality director", "qa director",
            "vp qa", "quality assurance", "chief quality",
            "vp qc", "quality control", "compliance officer",
            "head of compliance", "director compliance", "vp compliance",
            "chief compliance", "qms", "quality systems", "quality engineering"
        ],
        "manufacturing": [
            "vp manufacturing", "vice president manufacturing", "head of manufacturing",
            "director manufacturing", "manufacturing director", "plant manager",
            "plant director", "production director", "vp production",
            "head of production", "director production", "manufacturing operations",
            "production manager", "site manufacturing"
        ],
        "operations": [
            "vp operations", "vice president operations", "head of operations",
            "director operations", "operations director", "site director",
            "vp ops", "coo", "chief operating", "evp operations",
            "svp operations", "general manager", "site head"
        ],
        "it": [
            "cio", "chief information", "vp it", "vice president it",
            "it director", "director it", "head of it",
            "chief technology", "cto", "vp technology", "director technology",
            "head of technology", "it manager", "enterprise systems",
            "gxp systems", "csv", "computer systems validation",
            "validation manager", "director validation"
        ],
        "digital": [
            "vp digital", "vice president digital", "head of digital",
            "director digital", "digital transformation", "chief digital",
            "cdo", "vp automation", "director automation", "head of automation",
            "automation manager", "industry 4.0", "smart manufacturing",
            "digital manufacturing", "msat", "manufacturing science"
        ],
        "assets": [
            "vp maintenance", "director maintenance", "head of maintenance",
            "maintenance manager", "reliability", "vp reliability",
            "director reliability", "head of reliability", "asset management",
            "vp asset", "director asset", "calibration", "calibration manager",
            "director calibration", "equipment manager", "facilities",
            "cmms", "plant engineering"
        ],
        "regulatory": [
            "vp regulatory", "vice president regulatory", "head of regulatory",
            "director regulatory", "regulatory director", "regulatory affairs",
            "vp ra", "chief regulatory", "regulatory operations",
            "regulatory submissions", "regulatory strategy"
        ]
    }

    # Product eligibility by persona (SYNC WITH base_config.yaml)
    PERSONA_PRODUCTS = {
        "quality": {
            "eligible": ["qx"],
            "secondary": ["px", "rx"],
            "forbidden": ["mx", "ax"]
        },
        "manufacturing": {
            "eligible": ["mx"],
            "secondary": ["px", "ax"],
            "forbidden": ["qx", "rx"]
        },
        "operations": {
            "eligible": ["qx", "mx"],
            "secondary": ["px", "ax"],
            "forbidden": []
        },
        "it": {
            "eligible": ["qx", "mx", "px"],
            "secondary": ["ax"],
            "forbidden": ["rx"]
        },
        "digital": {
            "eligible": ["mx", "px"],
            "secondary": ["qx", "ax"],
            "forbidden": ["rx"]
        },
        "assets": {
            "eligible": ["ax"],
            "secondary": ["px", "mx"],
            "forbidden": ["qx", "rx"]
        },
        "regulatory": {
            "eligible": ["rx"],
            "secondary": ["qx"],
            "forbidden": ["mx", "ax", "px"]
        }
    }

    # Default persona when no match
    DEFAULT_PERSONA = "quality"

    # Pain library with tags
    PAIN_LIBRARY = {
        # Quality pains
        "capa_cycle_time": {
            "personas": ["quality"],
            "industries": ["pharma", "biotech", "medical_device"],
            "text": "I'm seeing QA teams pushed to shorten deviation and CAPA cycle time, but manual handoffs and training gaps keep approvals slow and increase audit risk.",
            "question": "How are you measuring deviation cycle time today, and is it trending the way you want?",
            "pain_area": "capa",
            "metrics": ["deviation cycle time", "CAPA closure time"]
        },

        "audit_readiness": {
            "personas": ["quality", "regulatory"],
            "industries": ["pharma", "biotech", "medical_device"],
            "text": "Most QA teams I work with are balancing two things: speeding up deviations and CAPA while also keeping audit readiness high. The friction shows up in documentation gaps and approval loops.",
            "question": "Is audit prep a planned focus this year, or already covered?",
            "pain_area": "audit_readiness",
            "metrics": ["audit findings", "documentation gaps"]
        },

        "supplier_oversight": {
            "personas": ["quality"],
            "industries": ["pharma", "biotech"],
            "text": "Sponsors are being held accountable for CMOs now, so supplier quality oversight is moving from annual audits to continuous visibility. Most biotech QA leaders tell me the challenge is audit record management and corrective action tracking across multiple CMOs.",
            "question": None,  # Goes straight to CTA
            "pain_area": "supplier_quality",
            "metrics": ["supplier audit frequency", "CMO oversight"]
        },

        # Operations pains
        "batch_release_time": {
            "personas": ["operations"],
            "industries": ["pharma", "biotech"],
            "text": "A lot of sites are trying to cut batch release time without adding headcount. The bottleneck I hear most is manual record review plus deviations that bounce between teams.",
            "question": "Is batch release a constraint for {company} right now, or already in a good place?",
            "pain_area": "batch_release",
            "metrics": ["batch release time", "review time"]
        },

        "review_by_exception": {
            "personas": ["operations", "quality"],
            "industries": ["pharma", "biotech"],
            "text": "A lot of plants are moving to review-by-exception for batch records, but the transition is slow because QA still reviews everything when deviations or out-of-spec events happen.",
            "question": "Is review-by-exception on your roadmap, or not a focus?",
            "pain_area": "batch_review",
            "metrics": ["QA review workload", "batch throughput"]
        },

        "training_effectiveness": {
            "personas": ["operations", "quality"],
            "industries": ["pharma", "biotech", "medical_device"],
            "text": "Most manufacturing sites tell me training completion rates look good on paper, but effectiveness is hard to measure, and retraining after deviations adds load without clear improvement.",
            "question": "Is training compliance tracking a focus this year, or already handled?",
            "pain_area": "training",
            "metrics": ["training completion", "training effectiveness"]
        },

        # IT pains
        "validation_load": {
            "personas": ["it"],
            "industries": ["pharma", "biotech", "medical_device"],
            "text": "When quality workflows live across too many tools, audit trails and access controls get messy, and every change feels like a validation project.",
            "question": "Are you trying to consolidate quality and manufacturing workflows this year, or leaving it decentralized?",
            "pain_area": "system_sprawl",
            "metrics": ["number of systems", "validation cost"]
        },

        "audit_trail_integrity": {
            "personas": ["it", "quality"],
            "industries": ["pharma", "biotech", "medical_device"],
            "text": "When quality workflows are split across multiple tools, audit trail integrity and access controls become a validation and compliance risk. Each system has its own logging and signature rules.",
            "question": "Are you consolidating quality workflows this year, or keeping the current setup?",
            "pain_area": "data_integrity",
            "metrics": ["audit trail gaps", "system integration"]
        },

        # Medical device specific
        "dhf_dmr_friction": {
            "personas": ["quality", "regulatory"],
            "industries": ["medical_device"],
            "text": "I work with other medical device component manufacturers. Most tell me the DHF, DMR, and traceability requirements create more friction than the actual engineering. Paper batch records and SharePoint-based change control tend to be where things slow down, especially when prepping for audits.",
            "question": None,  # Goes straight to CTA
            "pain_area": "design_control",
            "metrics": ["DHF cycle time", "design change duration"]
        }
    }

    # Regulatory trigger library
    TRIGGER_LIBRARY = {
        "qmsr_2026": {
            "industries": ["medical_device"],
            "active_until": "2026-02-02",
            "text": "With QMSR enforcement Feb 2, 2026, device QA teams are finding DHF gaps in change control and design history documentation.",
            "trigger_type": "regulatory_deadline"
        },

        "fda_inspection_climate": {
            "industries": ["pharma", "biotech", "medical_device"],
            "active_until": "2026-12-31",
            "text": "We're seeing more detailed FDA inspections this year, so documentation rigor around deviations and batch records is rising.",
            "trigger_type": "enforcement_climate"
        },

        "cmo_accountability": {
            "industries": ["pharma", "biotech"],
            "active_until": "2026-12-31",
            "text": "Sponsors are being held accountable for CMOs now, so supplier quality oversight is moving from annual visits to real-time visibility.",
            "trigger_type": "enforcement_climate"
        }
    }

    # CTA library with matching logic
    CTA_LIBRARY = {
        "capa": {
            "personas": ["quality"],
            "deliverable": "1-page checklist",
            "text": "If helpful, I can send a 1-page checklist QA leaders use to find the biggest time sinks in deviations, CAPA, and training. Want it?"
        },

        "audit_readiness": {
            "personas": ["quality", "regulatory"],
            "deliverable": "audit readiness self-check",
            "text": "I can send the 1-page checklist on deviation time sinks. Want it?"
        },

        "supplier_quality": {
            "personas": ["quality"],
            "deliverable": "supplier oversight pattern",
            "text": "Want the supplier oversight pattern, or already solved?"
        },

        "batch_release": {
            "personas": ["operations"],
            "deliverable": "benchmark sheet",
            "text": "If it helps, I can share a simple benchmark sheet of the 5 metrics ops leaders track when they attack release time. Want me to send it?"
        },

        "batch_review": {
            "personas": ["operations", "quality"],
            "deliverable": "benchmark",
            "text": "I can share the benchmark on the 5 metrics ops leaders track for release time. Want me to send it?"
        },

        "training": {
            "personas": ["operations", "quality"],
            "deliverable": "framework",
            "text": "Want the simple framework ops leaders use to connect training to deviation trends? Happy to send it."
        },

        "system_sprawl": {
            "personas": ["it"],
            "deliverable": "reference architecture",
            "text": "If useful, I can send a 1-page reference architecture teams use to scope QMS plus MES data flows without blowing up validation effort. Want it?"
        },

        "data_integrity": {
            "personas": ["it", "quality"],
            "deliverable": "reference architecture",
            "text": "I can send the 1-page reference architecture for QMS + MES data flows. Want it?"
        },

        "design_control": {
            "personas": ["quality", "regulatory"],
            "deliverable": "pattern",
            "text": "Should I share the design control pattern, or is this handled?"
        }
    }

    # Subject line library
    SUBJECT_LIBRARY = {
        "capa": ["CAPA backlog", "Deviation cycle time", "CAPA closure"],
        "audit_readiness": ["Audit readiness", "Audit prep", "Inspection prep"],
        "supplier_quality": ["Supplier audits", "CMO oversight", "Supplier quality"],
        "batch_release": ["Batch release time", "Batch release delays"],
        "batch_review": ["Review by exception", "Batch review"],
        "training": ["Training gaps", "Training compliance"],
        "system_sprawl": ["Validation load", "System sprawl", "QMS tech debt"],
        "data_integrity": ["Audit trails", "Data integrity"],
        "design_control": ["DHF cycle time", "Design control"]
    }

    def detect_persona(self, title: Optional[str]) -> Optional[str]:
        """
        Detect persona from job title.

        Args:
            title: Job title (e.g., "VP Quality")

        Returns:
            Persona key ("quality", "operations", "it", "regulatory") or None
        """
        if not title:
            return None

        title_lower = title.lower()

        for persona, patterns in self.PERSONA_PATTERNS.items():
            if any(pattern in title_lower for pattern in patterns):
                logger.info(f"Detected persona: {persona} from title '{title}'")
                return persona

        logger.warning(f"Could not detect persona from title '{title}'")
        return None

    def get_pains(
        self,
        persona: Optional[str],
        industry: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get relevant pain points based on persona and industry.

        Args:
            persona: Persona key (quality, operations, it, regulatory)
            industry: Industry (pharma, biotech, medical_device)
            limit: Max number of pains to return

        Returns:
            List of pain dicts sorted by relevance
        """
        if not persona:
            logger.warning("No persona provided, returning generic pains")
            persona = "quality"  # Default to quality

        matched_pains = []

        for pain_key, pain_data in self.PAIN_LIBRARY.items():
            # Check persona match
            if persona not in pain_data["personas"]:
                continue

            # Check industry match (if specified)
            if industry:
                industry_match = any(
                    ind in industry.lower()
                    for ind in pain_data["industries"]
                )
                if not industry_match:
                    continue

            matched_pains.append({
                "key": pain_key,
                **pain_data
            })

        logger.info(f"Found {len(matched_pains)} matching pains for persona={persona}, industry={industry}")

        return matched_pains[:limit]

    def get_triggers(
        self,
        industry: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get active regulatory triggers for industry.

        Args:
            industry: Industry (pharma, biotech, medical_device)

        Returns:
            List of active trigger dicts
        """
        if not industry:
            return []

        active_triggers = []
        today = datetime.now().date()

        for trigger_key, trigger_data in self.TRIGGER_LIBRARY.items():
            # Check industry match
            if industry:
                industry_match = any(
                    ind in industry.lower()
                    for ind in trigger_data["industries"]
                )
                if not industry_match:
                    continue

            # Check if still active
            active_until = datetime.strptime(
                trigger_data["active_until"],
                "%Y-%m-%d"
            ).date()

            if today <= active_until:
                active_triggers.append({
                    "key": trigger_key,
                    **trigger_data
                })

        logger.info(f"Found {len(active_triggers)} active triggers for industry={industry}")

        return active_triggers

    def get_cta(
        self,
        pain_area: str,
        persona: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get matching CTA for pain area and persona.

        Args:
            pain_area: Pain area key (capa, audit_readiness, etc.)
            persona: Persona key (quality, operations, it, regulatory)

        Returns:
            CTA dict or None
        """
        cta_data = self.CTA_LIBRARY.get(pain_area)

        if not cta_data:
            logger.warning(f"No CTA found for pain_area={pain_area}")
            return None

        # Check persona match if provided
        if persona and persona not in cta_data["personas"]:
            logger.warning(
                f"CTA for pain_area={pain_area} doesn't match persona={persona}"
            )

        logger.info(f"Selected CTA for pain_area={pain_area}")

        return cta_data

    def get_subject_line(self, pain_area: str) -> str:
        """
        Get subject line for pain area.

        Args:
            pain_area: Pain area key

        Returns:
            Subject line (first option from list)
        """
        subjects = self.SUBJECT_LIBRARY.get(pain_area, ["Quality initiative"])
        return subjects[0]

    def normalize_industry(self, raw_industry: Optional[str]) -> Optional[str]:
        """
        Normalize industry string to standard keys.

        Args:
            raw_industry: Raw industry string from research

        Returns:
            Normalized key (pharma, biotech, medical_device) or None
        """
        if not raw_industry:
            return None

        industry_lower = raw_industry.lower()

        # Mapping patterns
        if any(x in industry_lower for x in ["pharma", "pharmaceutical"]):
            return "pharma"
        elif any(x in industry_lower for x in ["biotech", "biotechnology"]):
            return "biotech"
        elif any(x in industry_lower for x in ["medical device", "medtech"]):
            return "medical_device"

        return None
