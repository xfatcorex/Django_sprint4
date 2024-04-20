from django.core.exceptions import ValidationError
from django.db import models


class ObsceneWords(models.Model):
    word = models.CharField(
        'Запрещенное слово',
        max_length=128
    )

    class Meta:
        verbose_name = 'запрещенное слово'
        verbose_name_plural = 'Запрещенные слова'

    def __str__(self):
        return self.word


def validate_words(text):
    obscene_words = ObsceneWords.objects.values_list('word', flat=True)
    for word in obscene_words:
        if word.lower() in text.lower():
            raise ValidationError(f'Слово "{word}" использовать нельзя')
