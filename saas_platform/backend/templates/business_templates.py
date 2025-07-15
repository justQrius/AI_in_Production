"""
Business idea templates for different industries and use cases.
Each template provides specialized prompts for generating relevant ideas.
"""

from typing import Dict

BUSINESS_TEMPLATES: Dict[str, Dict[str, str]] = {
    "general": {
        "name": "General Business",
        "description": "General business ideas across all industries",
        "prompt": "Generate a innovative business idea that could be built with AI technology. Include market analysis, target audience, and implementation strategy.",
        "icon": "💼"
    },

    "tech": {
        "name": "Technology & SaaS",
        "description": "Software and technology-focused business ideas",
        "prompt": "Generate an innovative SaaS or technology business idea. Focus on AI/ML applications, developer tools, or productivity software. Include tech stack recommendations, MVP features, and go-to-market strategy.",
        "icon": "💻"
    },

    "ecommerce": {
        "name": "E-commerce & Retail",
        "description": "Online retail and marketplace ideas",
        "prompt": "Generate an e-commerce business idea with a unique value proposition. Include niche selection, supplier strategy, marketing channels, and logistics considerations.",
        "icon": "🛒"
    },

    "healthcare": {
        "name": "Healthcare & Wellness",
        "description": "Health technology and wellness services",
        "prompt": "Generate a healthcare or wellness business idea leveraging AI. Focus on patient care, medical diagnosis assistance, wellness tracking, or telemedicine. Include regulatory considerations and privacy compliance.",
        "icon": "🏥"
    },

    "finance": {
        "name": "Fintech & Finance",
        "description": "Financial services and fintech innovations",
        "prompt": "Generate a fintech business idea that solves a real financial pain point. Include payment processing, investment management, or financial planning. Address security, compliance, and trust-building strategies.",
        "icon": "💰"
    },

    "saas": {
        "name": "B2B SaaS",
        "description": "Business-to-business software solutions",
        "prompt": "Generate a B2B SaaS business idea that improves business operations or productivity. Include enterprise features, pricing strategy, sales approach, and integration capabilities.",
        "icon": "🚀"
    },

    "marketplace": {
        "name": "Marketplace & Platform",
        "description": "Two-sided marketplace platforms",
        "prompt": "Generate a marketplace or platform business idea connecting buyers and sellers. Include network effects strategy, trust mechanisms, pricing model, and growth tactics.",
        "icon": "🤝"
    },

    "ai_agents": {
        "name": "AI Agents",
        "description": "Autonomous AI agent applications",
        "prompt": "Generate a business idea for an AI agent application. Focus on autonomous agents that can perform tasks, make decisions, or provide services. Include agent capabilities, use cases, and monetization strategy.",
        "icon": "🤖"
    },

    "education": {
        "name": "EdTech & Learning",
        "description": "Educational technology and e-learning",
        "prompt": "Generate an educational technology business idea. Focus on online learning, skill development, or certification programs. Include content strategy, instructor model, and student acquisition.",
        "icon": "📚"
    },

    "sustainability": {
        "name": "Climate & Sustainability",
        "description": "Environmental and sustainable businesses",
        "prompt": "Generate a sustainable or climate-focused business idea. Include environmental impact, carbon reduction strategies, circular economy principles, and ESG compliance.",
        "icon": "🌱"
    }
}


def get_template(template_key: str) -> Dict[str, str]:
    """
    Get a business template by key.

    Args:
        template_key: The template identifier

    Returns:
        Template dictionary or general template if not found
    """
    return BUSINESS_TEMPLATES.get(template_key, BUSINESS_TEMPLATES["general"])


def get_available_templates(tier_templates: list) -> Dict[str, Dict[str, str]]:
    """
    Get templates available for a subscription tier.

    Args:
        tier_templates: List of template keys available for the tier

    Returns:
        Dictionary of available templates
    """
    if tier_templates == "all":
        return BUSINESS_TEMPLATES

    return {
        key: template
        for key, template in BUSINESS_TEMPLATES.items()
        if key in tier_templates
    }


def list_all_templates() -> Dict[str, str]:
    """
    Get a simple list of all templates with names and descriptions.

    Returns:
        Dictionary mapping template keys to display info
    """
    return {
        key: {
            "name": template["name"],
            "description": template["description"],
            "icon": template["icon"]
        }
        for key, template in BUSINESS_TEMPLATES.items()
    }
