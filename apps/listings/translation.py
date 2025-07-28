from modeltranslation.translator import register, TranslationOptions
from .models import TextMessage

@register(TextMessage)
class TextMessageTranslationOptions(TranslationOptions):
    fields = ('text',)
