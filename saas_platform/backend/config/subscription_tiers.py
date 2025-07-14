"""
Subscription tier configuration for the SaaS platform.
Defines limits and features for each subscription level.
"""

from enum import Enum
from typing import Dict, Any


class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic_plan"
    PRO = "premium_subscription"
    ENTERPRISE = "enterprise_plan"


TIER_LIMITS: Dict[SubscriptionTier, Dict[str, Any]] = {
    SubscriptionTier.FREE: {
        "ideas_per_day": 3,
        "ideas_per_month": 30,
        "template_access": ["general"],
        "languages": ["en"],
        "priority_support": False,
        "analytics_access": False,
        "custom_prompts": False,
    },
    SubscriptionTier.BASIC: {
        "ideas_per_day": 20,
        "ideas_per_month": 300,
        "template_access": ["general", "tech", "ecommerce"],
        "languages": ["en", "es", "fr"],
        "priority_support": False,
        "analytics_access": True,
        "custom_prompts": False,
    },
    SubscriptionTier.PRO: {
        "ideas_per_day": 100,
        "ideas_per_month": 2000,
        "template_access": ["general", "tech", "ecommerce", "healthcare", "finance", "saas"],
        "languages": ["en", "es", "fr", "de", "it", "pt", "zh", "ja"],
        "priority_support": True,
        "analytics_access": True,
        "custom_prompts": True,
    },
    SubscriptionTier.ENTERPRISE: {
        "ideas_per_day": -1,  # Unlimited
        "ideas_per_month": -1,  # Unlimited
        "template_access": "all",
        "languages": "all",
        "priority_support": True,
        "analytics_access": True,
        "custom_prompts": True,
    },
}


def get_tier_limits(tier: str) -> Dict[str, Any]:
    """
    Get the limits for a specific subscription tier.

    Args:
        tier: The subscription tier key

    Returns:
        Dictionary containing tier limits and features
    """
    try:
        tier_enum = SubscriptionTier(tier)
        return TIER_LIMITS[tier_enum]
    except ValueError:
        # Default to free tier if tier is invalid
        return TIER_LIMITS[SubscriptionTier.FREE]


def can_generate_idea(tier: str, daily_count: int, monthly_count: int) -> tuple[bool, str]:
    """
    Check if a user can generate an idea based on their tier limits.

    Args:
        tier: The subscription tier
        daily_count: Number of ideas generated today
        monthly_count: Number of ideas generated this month

    Returns:
        Tuple of (can_generate, reason_if_not)
    """
    limits = get_tier_limits(tier)

    daily_limit = limits["ideas_per_day"]
    monthly_limit = limits["ideas_per_month"]

    # Check if unlimited
    if daily_limit == -1 and monthly_limit == -1:
        return True, ""

    # Check daily limit
    if daily_limit != -1 and daily_count >= daily_limit:
        return False, f"Daily limit reached ({daily_limit} ideas per day). Upgrade for more!"

    # Check monthly limit
    if monthly_limit != -1 and monthly_count >= monthly_limit:
        return False, f"Monthly limit reached ({monthly_limit} ideas per month). Upgrade for more!"

    return True, ""
