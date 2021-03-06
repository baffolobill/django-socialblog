# coding: utf-8

from django.contrib import admin

from socialblog.models import Post, Blog, BlogUserAccess


class BlogUserAccessInline(admin.TabularInline):
    model = BlogUserAccess


class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title', )}
    inlines = [BlogUserAccessInline, ]


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish', 'status')
    list_filter = ('publish', 'status')
    search_fields = ('title', 'body', 'tease')

admin.site.register(Blog, BlogAdmin)
admin.site.register(Post, PostAdmin)
