"""
Multi-language support configuration.
Defines supported languages and provides translation utilities.
"""

from typing import Dict

SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "name": "English",
        "native_name": "English",
        "flag": "🇺🇸",
        "prompt_suffix": "Generate the business idea in English."
    },
    "es": {
        "name": "Spanish",
        "native_name": "Español",
        "flag": "🇪🇸",
        "prompt_suffix": "Generate the business idea in Spanish."
    },
    "fr": {
        "name": "French",
        "native_name": "Français",
        "flag": "🇫🇷",
        "prompt_suffix": "Generate the business idea in French."
    },
    "de": {
        "name": "German",
        "native_name": "Deutsch",
        "flag": "🇩🇪",
        "prompt_suffix": "Generate the business idea in German."
    },
    "it": {
        "name": "Italian",
        "native_name": "Italiano",
        "flag": "🇮🇹",
        "prompt_suffix": "Generate the business idea in Italian."
    },
    "pt": {
        "name": "Portuguese",
        "native_name": "Português",
        "flag": "🇵🇹",
        "prompt_suffix": "Generate the business idea in Portuguese."
    },
    "zh": {
        "name": "Chinese",
        "native_name": "中文",
        "flag": "🇨🇳",
        "prompt_suffix": "Generate the business idea in Simplified Chinese."
    },
    "ja": {
        "name": "Japanese",
        "native_name": "日本語",
        "flag": "🇯🇵",
        "prompt_suffix": "Generate the business idea in Japanese."
    }
}


def get_language_info(lang_code: str) -> Dict[str, str]:
    """
    Get information about a language.

    Args:
        lang_code: ISO 639-1 language code

    Returns:
        Dictionary with language information
    """
    return SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES["en"])


def is_language_supported(lang_code: str, available_languages: list) -> bool:
    """
    Check if a language is supported for a subscription tier.

    Args:
        lang_code: ISO 639-1 language code
        available_languages: List of languages available for the tier

    Returns:
        True if language is supported, False otherwise
    """
    if available_languages == "all":
        return lang_code in SUPPORTED_LANGUAGES

    return lang_code in available_languages


def get_available_languages(tier_languages: list) -> Dict[str, Dict[str, str]]:
    """
    Get languages available for a subscription tier.

    Args:
        tier_languages: List of language codes or "all"

    Returns:
        Dictionary of available languages
    """
    if tier_languages == "all":
        return SUPPORTED_LANGUAGES

    return {
        code: info
        for code, info in SUPPORTED_LANGUAGES.items()
        if code in tier_languages
    }


def get_prompt_with_language(base_prompt: str, lang_code: str) -> str:
    """
    Append language instruction to a prompt.

    Args:
        base_prompt: The base prompt text
        lang_code: ISO 639-1 language code

    Returns:
        Prompt with language instruction
    """
    lang_info = get_language_info(lang_code)
    return f"{base_prompt}\n\n{lang_info['prompt_suffix']}"
