"""
Abstract base class for translation engines.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TranslationResult:
    """Result from a translation engine."""
    text: str
    source_lang: str
    target_lang: str
    backend: str  # e.g. 'libretranslate', 'deepl', 'gpt-4o-mini'
    latency_ms: float = 0


class AbstractTranslationEngine(ABC):
    """
    Abstract base for translation engines.

    Implementations:
    - LibreTranslateEngine: Local LibreTranslate server, default
    - DeepLEngine: DeepL API
    - GPTEngine: OpenAI GPT-4o-mini API
    - ArgosTranslateEngine: Direct Argos Translate, offline fallback
    """

    def __init__(self, name: str):
        self.name = name
        self._enabled = True

    @abstractmethod
    async def translate(
        self, text: str, source_lang: str, target_lang: str
    ) -> TranslationResult:
        """Translate text from source language to target language."""
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if this translation backend is available."""
        ...

    @abstractmethod
    async def warmup(self) -> None:
        """Warm up / initialize the engine."""
        ...

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    @abstractmethod
    def supported_languages(self) -> list[str]:
        """List of supported target language codes."""
        ...
