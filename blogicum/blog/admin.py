from django.contrib import admin

from .models import Category, Comment, Location, Post
from .validators import ObsceneWords

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Comment)
admin.site.register(ObsceneWords)
admin.site.empty_value_display = 'Не задано'
