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
    words_list = [word.lower() for word in text.split()]
    for word in words_list:
        if ObsceneWords.objects.filter(word=word).exists():
            raise ValidationError(f'Слово "{word}" использовать нельзя')
