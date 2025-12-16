"""
Context Synthesizer - Transforms research into email-ready context

Takes raw research data from ZoomInfo and Perplexity and synthesizes it into
structured context ready for email generation.

Usage:
    from context_synthesizer import ContextSynthesizer

    synthesizer = ContextSynthesizer()
    context = synthesizer.synthesize(research_results)
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContextSynthesizer:
    """
    Synthesizes raw research data into structured email context.

    Transforms ZoomInfo + Perplexity research into:
    - Contact profile (name, title, contact info)
    - Company profile (industry, size, tech stack, pains)
    - Triggers (recent events worth mentioning)
    - Email context (personalization hooks, pain points, specific references)
    """

    # Tech stack indicators of manual processes
    MANUAL_PROCESS_INDICATORS = [
        'sharepoint', 'excel', 'email', 'outlook', 'word', 'access',
        'filemaker', 'paper', 'manual', 'spreadsheet'
    ]

    # Tech stack indicators of quality systems
    QUALITY_SYSTEM_INDICATORS = [
        'trackwise', 'veeva', 'mastercontrol', 'arena', 'etq',
        'sparta', 'qms', 'eqms', 'lims', 'labware'
    ]

    # Industry-specific pain mapping
    INDUSTRY_PAIN_MAP = {
        'pharmaceuticals': [
            'FDA audit readiness',
            'data integrity across paper batch records',
            'CAPA backlog and closure times',
            'training compliance and effectiveness',
            'deviation investigation bottlenecks'
        ],
        'medical device': [
            'design control documentation',
            'supplier quality management',
            'post-market surveillance',
            'CAPA effectiveness',
            'complaint handling efficiency'
        ],
        'biotechnology': [
            'GMP documentation',
            'batch release delays',
            'process validation',
            'change control complexity',
            'audit trail compliance'
        ],
        'life sciences': [
            'regulatory compliance',
            'quality documentation',
            'audit preparation',
            'training management',
            'change control processes'
        ]
    }

    def synthesize(
        self,
        research: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize research into email-ready context.

        Args:
            research: Research results from ResearchOrchestrator with keys:
                - contact: ZoomInfo contact data
                - company: ZoomInfo company data
                - perplexity: Perplexity research
                - errors: List of errors

        Returns:
            {
                'contact_profile': {
                    'first_name': str,
                    'last_name': str,
                    'title': str,
                    'company': str,
                    'email': str or None,
                    'phone': str or None
                },
                'company_profile': {
                    'industry': str or None,
                    'size': str or None,
                    'revenue': str or None,
                    'tech_stack': [str],
                    'likely_pains': [str],
                    'manual_processes_detected': bool
                },
                'triggers': [
                    {
                        'type': str (news|hiring|funding|acquisition|fda|leadership),
                        'description': str,
                        'relevance': str (why it matters)
                    }
                ],
                'email_context': {
                    'personalization_hooks': [str] (3-5 specific references),
                    'primary_pain': str (most relevant pain point),
                    'secondary_pains': [str] (2-3 additional pains),
                    'specific_reference': str (for opening line),
                    'business_problem': str (for body)
                },
                'synthesis_quality': {
                    'contact_found': bool,
                    'company_data_available': bool,
                    'triggers_found': int,
                    'confidence': str (high|medium|low)
                }
            }
        """
        logger.info("Starting context synthesis")

        # Extract contact profile
        contact_profile = self._extract_contact_profile(research.get('contact'), research)

        # Extract company profile
        company_profile = self._extract_company_profile(
            research.get('company'),
            research.get('perplexity'),
            research.get('webfetch')
        )

        # Identify triggers
        triggers = self._identify_triggers(
            research.get('perplexity'),
            contact_profile
        )

        # Generate email context
        email_context = self._generate_email_context(
            contact_profile,
            company_profile,
            triggers,
            research.get('perplexity')
        )

        # Assess synthesis quality
        synthesis_quality = self._assess_quality(
            research,
            contact_profile,
            company_profile,
            triggers
        )

        result = {
            'contact_profile': contact_profile,
            'company_profile': company_profile,
            'triggers': triggers,
            'email_context': email_context,
            'synthesis_quality': synthesis_quality
        }

        logger.info(
            f"Synthesis complete. Quality: {synthesis_quality['confidence']}, "
            f"Triggers: {len(triggers)}"
        )

        return result

    def _extract_contact_profile(
        self,
        contact_data: Optional[Dict[str, Any]],
        research_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract contact profile from ZoomInfo data with fallback to research.

        Args:
            contact_data: ZoomInfo contact dict or None
            research_data: Full research dict (for title extraction fallback)

        Returns:
            Contact profile dict
        """
        if not contact_data:
            contact_profile = {
                'first_name': '[First Name]',
                'last_name': '[Last Name]',
                'title': None,
                'company': None,
                'email': None,
                'phone': None
            }
        else:
            contact_profile = {
                'first_name': contact_data.get('first_name', '[First Name]'),
                'last_name': contact_data.get('last_name', '[Last Name]'),
                'title': contact_data.get('title'),
                'company': contact_data.get('company_name'),
                'email': contact_data.get('email'),
                'phone': contact_data.get('phone')
            }

        # Extract title from research if not found in ZoomInfo
        if not contact_profile.get('title') and research_data:
            import re
            perplexity = research_data.get('perplexity', {})

            # Look for title patterns in contact-related text
            title_patterns = [
                r'\b(VP|Vice President|Director|Manager|Head of|Chief|Senior)\s+(?:of\s+)?(\w+(?:\s+\w+)*)',
                r'\b(Quality|Manufacturing|Operations|Engineering|Regulatory)\s+(VP|Director|Manager|Lead)',
            ]

            # Search in company overview and news
            texts_to_search = [
                perplexity.get('company_overview', ''),
                perplexity.get('company_news', [''])[0] if perplexity.get('company_news') else ''
            ]

            for text in texts_to_search:
                for pattern in title_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        contact_profile['title'] = match.group(0)
                        break
                if contact_profile.get('title'):
                    break

        return contact_profile

    def _extract_company_profile(
        self,
        company_data: Optional[Dict[str, Any]],
        perplexity_data: Optional[Dict[str, Any]],
        webfetch_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract company profile from ZoomInfo + Perplexity + WebFetch data.

        Args:
            company_data: ZoomInfo company dict
            perplexity_data: Perplexity research dict
            webfetch_data: WebFetch research dict (website data extraction)

        Returns:
            Company profile dict
        """
        profile = {
            'industry': None,
            'size': None,
            'revenue': None,
            'tech_stack': [],
            'likely_pains': [],
            'manual_processes_detected': False
        }

        # Extract from ZoomInfo company data
        if company_data:
            profile['industry'] = company_data.get('industry')
            profile['revenue'] = company_data.get('revenue')
            profile['size'] = company_data.get('employee_count')
            profile['tech_stack'] = company_data.get('tech_stack', [])

            # Check for manual process indicators
            tech_stack_lower = [tech.lower() for tech in profile['tech_stack']]
            profile['manual_processes_detected'] = any(
                indicator in tech_stack_lower
                for indicator in self.MANUAL_PROCESS_INDICATORS
            )

        # Infer pains from industry
        if profile['industry']:
            industry_lower = profile['industry'].lower()
            for key, pains in self.INDUSTRY_PAIN_MAP.items():
                if key in industry_lower:
                    profile['likely_pains'].extend(pains)
                    break

        # Add pains from Perplexity research (with sanitization)
        if perplexity_data:
            if perplexity_data.get('business_challenges'):
                challenges = perplexity_data['business_challenges']
                if isinstance(challenges, list):
                    # Sanitize each challenge
                    valid_challenges = [
                        c.strip() for c in challenges[:3]
                        if self._is_valid_trigger_text(c)
                    ]
                    profile['likely_pains'].extend(valid_challenges)
                elif isinstance(challenges, str) and self._is_valid_trigger_text(challenges):
                    profile['likely_pains'].append(challenges.strip())

            if perplexity_data.get('role_specific_pains'):
                pains = perplexity_data['role_specific_pains']
                if isinstance(pains, list):
                    # Sanitize each pain
                    valid_pains = [
                        p.strip() for p in pains[:2]
                        if self._is_valid_trigger_text(p)
                    ]
                    profile['likely_pains'].extend(valid_pains)
                elif isinstance(pains, str) and self._is_valid_trigger_text(pains):
                    profile['likely_pains'].append(pains.strip())

        # Add data from WebFetch research
        if webfetch_data:
            # Use industries from webfetch if not found elsewhere
            if not profile['industry'] and webfetch_data.get('industries'):
                profile['industry'] = ', '.join(webfetch_data['industries'][:2])

            # Add regulatory keywords as pain indicators
            if webfetch_data.get('regulatory_keywords'):
                for keyword in webfetch_data['regulatory_keywords']:
                    if 'fda' in keyword.lower():
                        profile['likely_pains'].append('FDA audit readiness and compliance')
                    elif 'iso' in keyword.lower():
                        profile['likely_pains'].append('ISO certification and quality management')

        # Deduplicate and limit pains
        profile['likely_pains'] = list(set(profile['likely_pains']))[:5]

        # Default pain if none found
        if not profile['likely_pains']:
            profile['likely_pains'] = ['quality and compliance challenges']

        return profile

    def _is_valid_trigger_text(self, text: str) -> bool:
        """
        Check if trigger text is valid (not placeholder junk).

        Args:
            text: Text to validate

        Returns:
            True if valid, False if placeholder/junk
        """
        if not text or not isinstance(text, str):
            return False

        # Strip whitespace
        text_stripped = text.strip()

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
        if len(text_stripped) < 5:
            return False

        return True

    def _identify_triggers(
        self,
        perplexity_data: Optional[Dict[str, Any]],
        contact_profile: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Identify trigger events worth mentioning in email.

        Args:
            perplexity_data: Perplexity research dict
            contact_profile: Contact profile dict

        Returns:
            List of trigger dicts (sanitized - no placeholder junk)
        """
        triggers = []

        if not perplexity_data:
            return triggers

        # Company news triggers
        if perplexity_data.get('company_news'):
            news_text = perplexity_data['company_news']

            # Handle both string and list formats
            if isinstance(news_text, str):
                news_items = [news_text]
            elif isinstance(news_text, list):
                news_items = news_text
            else:
                news_items = []

            for news in news_items[:2]:
                # Sanitize: skip invalid text
                if not self._is_valid_trigger_text(news):
                    continue

                company_name = contact_profile.get('company') or 'company'
                triggers.append({
                    'type': 'news',
                    'description': news.strip(),
                    'text': news.strip(),  # For backward compatibility
                    'source_url': f"https://www.google.com/search?q={company_name}+news",
                    'relevance': 'Recent company activity suggests change or growth'
                })

        # Recent initiatives
        if perplexity_data.get('recent_initiatives'):
            initiatives_text = perplexity_data['recent_initiatives']

            # Handle both string and list formats
            if isinstance(initiatives_text, str):
                initiative_items = [initiatives_text]
            elif isinstance(initiatives_text, list):
                initiative_items = initiatives_text
            else:
                initiative_items = []

            for initiative in initiative_items[:2]:
                # Sanitize: skip invalid text
                if not self._is_valid_trigger_text(initiative):
                    continue

                company_name = contact_profile.get('company') or 'company'
                # Create a search-friendly snippet from initiative text
                search_snippet = initiative[:30] if len(initiative) > 30 else initiative
                triggers.append({
                    'type': 'initiative',
                    'description': initiative.strip(),
                    'text': initiative.strip(),  # For backward compatibility
                    'source_url': f"https://www.google.com/search?q={company_name}+{search_snippet}",
                    'relevance': 'Strategic initiative may create quality/compliance needs'
                })

        # Check for leadership change (new hire)
        if contact_profile.get('title') and 'vp' in contact_profile['title'].lower():
            company_name = contact_profile.get('company') or 'company'
            description = f"New {contact_profile['title']} at {company_name}"
            # Use LinkedIn company page as source for leadership changes
            linkedin_company = company_name.lower().replace(' ', '-').replace('&', 'and')
            triggers.append({
                'type': 'leadership',
                'description': description,
                'text': description,  # For backward compatibility
                'source_url': f"https://www.linkedin.com/company/{linkedin_company}",
                'relevance': 'New leader may be evaluating systems and processes'
            })

        return triggers[:3]  # Limit to top 3 triggers

    def _generate_email_context(
        self,
        contact_profile: Dict[str, Any],
        company_profile: Dict[str, Any],
        triggers: List[Dict[str, str]],
        perplexity_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate email-specific context (hooks, pains, references).

        Args:
            contact_profile: Contact profile dict
            company_profile: Company profile dict
            triggers: List of trigger events
            perplexity_data: Perplexity research dict

        Returns:
            Email context dict
        """
        context = {
            'personalization_hooks': [],
            'primary_pain': None,
            'secondary_pains': [],
            'specific_reference': None,
            'business_problem': None
        }

        # Build personalization hooks
        hooks = []

        # Hook: Recent move to company
        if contact_profile.get('title') and 'vp' in contact_profile['title'].lower():
            hooks.append(
                f"Recent move to {contact_profile['company']}"
            )

        # Hook: Industry/role combination
        if contact_profile.get('title') and company_profile.get('industry'):
            hooks.append(
                f"{company_profile['industry']} {contact_profile['title']} background"
            )

        # Hook: Trigger events
        for trigger in triggers[:2]:
            if trigger['type'] in ['news', 'initiative']:
                hooks.append(trigger['description'][:80])

        # Hook: Tech stack (manual processes)
        if company_profile['manual_processes_detected']:
            hooks.append("Manual processes detected in tech stack")

        context['personalization_hooks'] = hooks[:4]

        # Select primary pain
        if company_profile['likely_pains']:
            context['primary_pain'] = company_profile['likely_pains'][0]
            context['secondary_pains'] = company_profile['likely_pains'][1:3]

        # Generate specific reference for opening line
        if triggers:
            context['specific_reference'] = triggers[0]['description']
        elif contact_profile.get('title'):
            context['specific_reference'] = (
                f"Saw your role as {contact_profile['title']} at {contact_profile['company']}"
            )
        else:
            context['specific_reference'] = None

        # Generate business problem statement
        if context['primary_pain']:
            if triggers:
                context['business_problem'] = (
                    f"{context['primary_pain']} following {triggers[0]['type']}"
                )
            else:
                context['business_problem'] = context['primary_pain']

        return context

    def _assess_quality(
        self,
        research: Dict[str, Any],
        contact_profile: Dict[str, Any],
        company_profile: Dict[str, Any],
        triggers: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Assess synthesis quality for confidence scoring.

        Args:
            research: Original research dict
            contact_profile: Extracted contact profile
            company_profile: Extracted company profile
            triggers: Identified triggers

        Returns:
            Quality assessment dict
        """
        quality = {
            'contact_found': False,
            'company_data_available': False,
            'triggers_found': len(triggers),
            'confidence': 'low'
        }

        # Check if contact was found
        if research.get('contact') and contact_profile.get('email'):
            quality['contact_found'] = True

        # Check if company data is available
        if research.get('company') or (
            company_profile.get('industry') and company_profile.get('likely_pains')
        ):
            quality['company_data_available'] = True

        # Calculate confidence
        score = 0
        if quality['contact_found']:
            score += 40
        if quality['company_data_available']:
            score += 30
        if quality['triggers_found'] > 0:
            score += 15 * min(quality['triggers_found'], 2)

        if score >= 70:
            quality['confidence'] = 'high'
        elif score >= 40:
            quality['confidence'] = 'medium'
        else:
            quality['confidence'] = 'low'

        return quality


def format_research_brief(context: Dict[str, Any]) -> str:
    """
    Format synthesized context into markdown research brief.

    Args:
        context: Synthesized context from ContextSynthesizer

    Returns:
        Markdown formatted research brief
    """
    contact = context['contact_profile']
    company = context['company_profile']
    triggers = context['triggers']
    email_ctx = context['email_context']
    quality = context['synthesis_quality']

    brief = f"""# Prospect Research: {contact['first_name']} {contact['last_name']}
Date: {datetime.utcnow().strftime('%Y-%m-%d')}

## Contact Profile
- Name: {contact['first_name']} {contact['last_name']}
- Title: {contact.get('title') or 'Unknown'}
- Email: {contact.get('email') or 'Not found'}
- Phone: {contact.get('phone') or 'Not found'}
- Company: {contact.get('company') or 'Unknown'}

## Company Profile
- Industry: {company.get('industry') or 'Unknown'}
- Size: {company.get('size') or 'Unknown'}
- Revenue: {company.get('revenue') or 'Unknown'}
- Tech Stack: {', '.join(company['tech_stack'][:5]) if company['tech_stack'] else 'Unknown'}
- Manual Processes: {'Yes' if company['manual_processes_detected'] else 'No'}

## Likely Pain Points
"""
    for pain in company['likely_pains']:
        brief += f"- {pain}\n"

    if triggers:
        brief += "\n## Triggers\n"
        for trigger in triggers:
            brief += f"- [{trigger['type'].upper()}] {trigger['description']}\n"

    brief += f"\n## Email Context\n"
    if email_ctx['specific_reference']:
        brief += f"- Opening Reference: {email_ctx['specific_reference']}\n"
    if email_ctx['primary_pain']:
        brief += f"- Primary Pain: {email_ctx['primary_pain']}\n"
    if email_ctx['personalization_hooks']:
        brief += f"- Personalization Hooks:\n"
        for hook in email_ctx['personalization_hooks']:
            brief += f"  - {hook}\n"

    brief += f"\n## Research Quality\n"
    brief += f"- Confidence: {quality['confidence'].upper()}\n"
    brief += f"- Contact Found: {'Yes' if quality['contact_found'] else 'No'}\n"
    brief += f"- Company Data: {'Yes' if quality['company_data_available'] else 'No'}\n"
    brief += f"- Triggers Found: {quality['triggers_found']}\n"

    return brief
