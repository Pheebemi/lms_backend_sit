from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Tag, Post, Comment, PostView


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'published_at', 'views', 'likes']
    list_filter = ['status', 'category', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['views', 'likes', 'created_at', 'updated_at']
    date_hierarchy = 'published_at'
    ordering = ['-created_at']
    actions = ['make_published', 'make_draft', 'make_archived']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('SEO', {
            'fields': ('meta_description',)
        }),
        ('Status & Dates', {
            'fields': ('status', 'published_at', 'created_at', 'updated_at')
        }),
        ('Engagement', {
            'fields': ('views', 'likes'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new post
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def make_published(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} posts were successfully published.')
    make_published.short_description = "Mark selected posts as published"
    
    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} posts were marked as draft.')
    make_draft.short_description = "Mark selected posts as draft"
    
    def make_archived(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} posts were archived.')
    make_archived.short_description = "Archive selected posts"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['name', 'email', 'content', 'post__title']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post')


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ['post', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['post__title', 'ip_address']
    readonly_fields = ['viewed_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post')
