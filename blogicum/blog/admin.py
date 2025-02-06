from django.contrib import admin

from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'is_published',
        'created_at',
        'slug'
    )
    list_filter = (
        'title',
    )
    search_fields = (
        'title',
    )


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'created_at',
        'is_published'
    )
    list_filter = (
        'name',
    )
    search_fields = (
        'name',
    )


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'category',
        'location'
    )
    list_filter = (
        'author',
        'category',
        'location'
    )
    search_fields = (
        'title',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
