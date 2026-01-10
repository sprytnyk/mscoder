"""Translations module for MSCoder."""

from . import en, uk


def get_translations(lang: str):
    """Get translation module for specified language."""
    return {"en": en, "uk": uk}.get(lang, en)


__all__ = ["en", "uk", "get_translations"]
