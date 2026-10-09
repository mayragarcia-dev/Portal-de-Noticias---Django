from django.contrib import admin
from .models import Article, Category, Author


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['user', 'website', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'bio']
    raw_id_fields = ['user']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'status', 'published_at', 'created_at']
    list_filter = ['status', 'category', 'author', 'published_at']
    search_fields = ['title', 'summary', 'content']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['category', 'author']
    date_hierarchy = 'published_at'
    ordering = ['-published_at', '-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'summary', 'content', 'featured_image')
        }),
        ('Publicación', {
            'fields': ('status', 'category', 'author', 'published_at')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )