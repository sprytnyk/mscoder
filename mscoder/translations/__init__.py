"""Translations module for MSCoder."""

from .en import TRANSLATIONS as EN_TRANSLATIONS
from .uk import TRANSLATIONS as UK_TRANSLATIONS

TRANSLATIONS = {
    "en": EN_TRANSLATIONS,
    "uk": UK_TRANSLATIONS,
}

__all__ = ["TRANSLATIONS"]
