from apps.listings.models import *
from modeltranslation.translator import translator, TranslationOptions


class TextMessageTranslationOptions(TranslationOptions):
    fields = ('text',)


translator.register(TextMessage, TextMessageTranslationOptions)