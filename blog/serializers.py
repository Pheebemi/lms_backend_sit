from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Tag, Post, Comment, PostView

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'post_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()


class TagSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'post_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class PostListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    excerpt = serializers.SerializerMethodField()
    read_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'category', 'tags',
            'excerpt', 'featured_image', 'status', 'published_at',
            'views', 'likes', 'read_time', 'created_at'
        ]
        read_only_fields = ['id', 'views', 'likes', 'created_at']
    
    def get_excerpt(self, obj):
        if obj.excerpt:
            return obj.excerpt
        # Generate excerpt from content if no excerpt provided
        content = obj.content[:200]
        return content + "..." if len(obj.content) > 200 else content
    
    def get_read_time(self, obj):
        # Estimate reading time (average 200 words per minute)
        word_count = len(obj.content.split())
        read_time = max(1, word_count // 200)
        return f"{read_time} min read"


class PostDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    read_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'category', 'tags',
            'excerpt', 'content', 'featured_image', 'meta_description',
            'status', 'published_at', 'views', 'likes', 'read_time',
            'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'views', 'likes', 'created_at', 'updated_at']
    
    def get_comments(self, obj):
        approved_comments = obj.comments.filter(is_approved=True)
        return CommentSerializer(approved_comments, many=True).data
    
    def get_read_time(self, obj):
        word_count = len(obj.content.split())
        read_time = max(1, word_count // 200)
        return f"{read_time} min read"


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'title', 'slug', 'category', 'tags', 'excerpt', 'content',
            'featured_image', 'meta_description', 'status'
        ]
    
    def create(self, validated_data):
        # Set the author to the current user
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'name', 'email', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']
    
    def create(self, validated_data):
        validated_data['post'] = self.context['post']
        return super().create(validated_data)


class PostViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostView
        fields = ['ip_address', 'viewed_at']
        read_only_fields = ['viewed_at']


class BlogStatsSerializer(serializers.Serializer):
    total_posts = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_tags = serializers.IntegerField()
    total_views = serializers.IntegerField()
    popular_posts = PostListSerializer(many=True, read_only=True)
    recent_posts = PostListSerializer(many=True, read_only=True)
    categories_with_counts = CategorySerializer(many=True, read_only=True)
