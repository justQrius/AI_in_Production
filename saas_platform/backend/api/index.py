import os
from fastapi import FastAPI, Depends, HTTPException, Query  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from pydantic import BaseModel  # type: ignore
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials  # type: ignore
from openai import OpenAI  # type: ignore
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from config.subscription_tiers import get_tier_limits, can_generate_idea
from middleware.usage_tracker import usage_tracker
from templates.business_templates import get_template, list_all_templates, get_available_templates
from i18n.languages import get_prompt_with_language, get_available_languages, is_language_supported

app = FastAPI()

clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)


class IdeaRequest(BaseModel):
    template: Optional[str] = "general"
    language: Optional[str] = "en"
    custom_prompt: Optional[str] = None


@app.get("/api/templates")
def get_templates(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    """Get available templates based on user's subscription tier."""
    user_id = creds.decoded["sub"]
    subscription_plan = creds.decoded.get("org_role", "free")  # Default to free if not specified

    tier_limits = get_tier_limits(subscription_plan)
    available_templates = get_available_templates(tier_limits["template_access"])

    return {
        "templates": available_templates,
        "tier": subscription_plan
    }


@app.get("/api/languages")
def get_languages(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    """Get available languages based on user's subscription tier."""
    user_id = creds.decoded["sub"]
    subscription_plan = creds.decoded.get("org_role", "free")

    tier_limits = get_tier_limits(subscription_plan)
    available_languages = get_available_languages(tier_limits["languages"])

    return {
        "languages": available_languages,
        "tier": subscription_plan
    }


@app.get("/api/usage")
def get_usage(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    """Get usage statistics for the current user."""
    user_id = creds.decoded["sub"]
    subscription_plan = creds.decoded.get("org_role", "free")

    stats = usage_tracker.get_usage_stats(user_id)
    tier_limits = get_tier_limits(subscription_plan)

    # Calculate remaining ideas
    daily_limit = tier_limits["ideas_per_day"]
    monthly_limit = tier_limits["ideas_per_month"]

    remaining_today = None if daily_limit == -1 else max(0, daily_limit - stats["daily_ideas"])
    remaining_month = None if monthly_limit == -1 else max(0, monthly_limit - stats["monthly_ideas"])

    return {
        "usage": stats,
        "limits": {
            "daily_limit": "unlimited" if daily_limit == -1 else daily_limit,
            "monthly_limit": "unlimited" if monthly_limit == -1 else monthly_limit,
            "remaining_today": "unlimited" if remaining_today is None else remaining_today,
            "remaining_month": "unlimited" if remaining_month is None else remaining_month
        },
        "tier": subscription_plan
    }


@app.get("/api/analytics")
def get_analytics(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    """Get detailed analytics for the current user."""
    user_id = creds.decoded["sub"]
    subscription_plan = creds.decoded.get("org_role", "free")

    tier_limits = get_tier_limits(subscription_plan)

    # Check if analytics is available for this tier
    if not tier_limits.get("analytics_access", False):
        raise HTTPException(status_code=403, detail="Analytics not available in your tier. Upgrade to access!")

    analytics = usage_tracker.get_analytics(user_id)

    return {
        "analytics": analytics,
        "tier": subscription_plan
    }


@app.post("/api")
def idea(
    request: IdeaRequest,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
):
    """Generate a business idea with template and language support."""
    user_id = creds.decoded["sub"]
    subscription_plan = creds.decoded.get("org_role", "free")

    # Get tier limits
    tier_limits = get_tier_limits(subscription_plan)

    # Get current usage
    stats = usage_tracker.get_usage_stats(user_id)

    # Check if user can generate an idea
    can_generate, reason = can_generate_idea(
        subscription_plan,
        stats["daily_ideas"],
        stats["monthly_ideas"]
    )

    if not can_generate:
        raise HTTPException(status_code=429, detail=reason)

    # Validate template access
    if request.template not in tier_limits["template_access"] and tier_limits["template_access"] != "all":
        raise HTTPException(
            status_code=403,
            detail=f"Template '{request.template}' not available in your tier. Upgrade to access more templates!"
        )

    # Validate language access
    if not is_language_supported(request.language, tier_limits["languages"]):
        raise HTTPException(
            status_code=403,
            detail=f"Language '{request.language}' not available in your tier. Upgrade for more languages!"
        )

    # Validate custom prompt access
    if request.custom_prompt and not tier_limits.get("custom_prompts", False):
        raise HTTPException(
            status_code=403,
            detail="Custom prompts not available in your tier. Upgrade to Pro or Enterprise!"
        )

    # Get template
    template = get_template(request.template)

    # Build prompt
    if request.custom_prompt and tier_limits.get("custom_prompts", False):
        base_prompt = request.custom_prompt
    else:
        base_prompt = template["prompt"]

    # Add language instruction
    final_prompt = get_prompt_with_language(base_prompt, request.language)

    # Generate idea
    client = OpenAI()
    prompt = [{"role": "user", "content": final_prompt}]
    stream = client.chat.completions.create(model="gpt-4o-mini", messages=prompt, stream=True)

    # Track usage
    usage_tracker.track_idea_generation(
        user_id,
        template=request.template,
        language=request.language
    )

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "saas-platform-api"}
