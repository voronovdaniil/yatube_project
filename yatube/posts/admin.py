from django.contrib import admin
from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    list_editable = ('group',)
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('text',)
    # Добавляем возможность фильтрации по дате
    list_filter = ('pub_date',)
    # Это свойство сработает для всех колонок: где пусто — там будет эта строка
    empty_value_display = '-пусто-'

class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description')
    search_fields = ('text',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'

admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)