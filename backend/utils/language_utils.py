"""
Language code mapping, validation, and auto-detection utilities.
"""

# Language code → display name
LANGUAGE_MAP = {
    "auto": "自动检测",
    "zh": "中文",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "pt": "Português",
    "ru": "Русский",
    "ar": "العربية",
    "hi": "हिन्दी",
    "th": "ไทย",
    "vi": "Tiếng Việt",
    "id": "Bahasa Indonesia",
}

# Whisper language codes that differ from standard codes
WHISPER_LANG_MAP = {
    "zh": "zh",
    "ja": "ja",
    "ko": "ko",
    "en": "en",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "pt": "pt",
    "ru": "ru",
    "ar": "ar",
    "hi": "hi",
    "th": "th",
    "vi": "vi",
    "id": "id",
}

# LibreTranslate language codes
LIBRETRANSLATE_LANG_MAP = {
    "zh": "zh",
    "en": "en",
    "ja": "ja",
    "ko": "ko",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "pt": "pt",
    "ru": "ru",
    "ar": "ar",
    "hi": "hi",
    "th": "th",
    "vi": "vi",
    "id": "id",
}


def get_display_name(lang_code: str) -> str:
    """Get display name for a language code."""
    return LANGUAGE_MAP.get(lang_code, lang_code)


def validate_lang_code(code: str) -> bool:
    """Check if a language code is supported."""
    return code in LANGUAGE_MAP or code == "auto"


def to_whisper_lang(code: str) -> str:
    """Convert standard language code to Whisper-compatible code."""
    return WHISPER_LANG_MAP.get(code, code)


def to_libretranslate_lang(code: str) -> str:
    """Convert standard language code to LibreTranslate-compatible code."""
    return LIBRETRANSLATE_LANG_MAP.get(code, code)


def get_supported_languages() -> list[dict]:
    """Get list of supported languages for the UI."""
    return [
        {"code": code, "name": name}
        for code, name in LANGUAGE_MAP.items()
        if code != "auto"
    ]
