from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Category, Tag, Post, Comment, PostView
from .serializers import (
    CategorySerializer, TagSerializer, PostListSerializer, 
    PostDetailSerializer, PostCreateUpdateSerializer,
    CommentSerializer, CommentCreateSerializer, BlogStatsSerializer
)


class BlogPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50


# Public Views (No Authentication Required)
class PostListView(generics.ListAPIView):
    """Public view to list all published blog posts"""
    serializer_class = PostListSerializer
    pagination_class = BlogPagination
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Post.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags')
        
        # Filter by category
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by tag
        tag_slug = self.request.query_params.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(excerpt__icontains=search)
            )
        
        return queryset.order_by('-published_at')


class PostDetailView(generics.RetrieveAPIView):
    """Public view to get a single published blog post"""
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track view
        client_ip = self.get_client_ip()
        PostView.objects.get_or_create(
            post=instance,
            ip_address=client_ip,
            defaults={'user_agent': request.META.get('HTTP_USER_AGENT', '')}
        )
        
        # Increment view count
        instance.increment_views()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class CategoryListView(generics.ListAPIView):
    """Public view to list all categories with post counts"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Category.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(post_count__gt=0).order_by('name')


class TagListView(generics.ListAPIView):
    """Public view to list all tags with post counts"""
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Tag.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(post_count__gt=0).order_by('name')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def blog_stats(request):
    """Get blog statistics for homepage"""
    total_posts = Post.objects.filter(status='published').count()
    total_categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0).count()
    total_tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0).count()
    total_views = Post.objects.aggregate(
        total_views=Sum('views')
    )['total_views'] or 0
    
    popular_posts = Post.objects.filter(
        status='published'
    ).order_by('-views')[:5]
    
    recent_posts = Post.objects.filter(
        status='published'
    ).order_by('-published_at')[:5]
    
    categories_with_counts = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0).order_by('-post_count')[:10]
    
    stats_data = {
        'total_posts': total_posts,
        'total_categories': total_categories,
        'total_tags': total_tags,
        'total_views': total_views,
        'popular_posts': popular_posts,
        'recent_posts': recent_posts,
        'categories_with_counts': categories_with_counts,
    }
    
    serializer = BlogStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def add_comment(request, post_slug):
    """Add a comment to a blog post"""
    post = get_object_or_404(Post, slug=post_slug, status='published')
    serializer = CommentCreateSerializer(data=request.data, context={'post': post})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin Views (Authentication Required)
class AdminPostListCreateView(generics.ListCreateAPIView):
    """Admin view to list and create blog posts"""
    serializer_class = PostCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    pagination_class = BlogPagination
    
    def get_queryset(self):
        return Post.objects.select_related('author', 'category').prefetch_related('tags').order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AdminPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin view to get, update, or delete a blog post"""
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get_queryset(self):
        return Post.objects.select_related('author', 'category').prefetch_related('tags')


class AdminCategoryListCreateView(generics.ListCreateAPIView):
    """Admin view to list and create categories"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get_queryset(self):
        return Category.objects.all().order_by('name')


class AdminTagListCreateView(generics.ListCreateAPIView):
    """Admin view to list and create tags"""
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get_queryset(self):
        return Tag.objects.all().order_by('name')


class AdminCommentListView(generics.ListAPIView):
    """Admin view to list all comments"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    pagination_class = BlogPagination
    
    def get_queryset(self):
        return Comment.objects.select_related('post').order_by('-created_at')


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def approve_comment(request, comment_id):
    """Approve or disapprove a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = not comment.is_approved
    comment.save()
    
    serializer = CommentSerializer(comment)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def admin_blog_stats(request):
    """Get detailed blog statistics for admin dashboard"""
    from django.db.models import Sum
    
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(status='published').count()
    draft_posts = Post.objects.filter(status='draft').count()
    total_views = Post.objects.aggregate(total_views=Sum('views'))['total_views'] or 0
    total_comments = Comment.objects.count()
    approved_comments = Comment.objects.filter(is_approved=True).count()
    
    recent_posts = Post.objects.order_by('-created_at')[:5]
    popular_posts = Post.objects.order_by('-views')[:5]
    pending_comments = Comment.objects.filter(is_approved=False).order_by('-created_at')[:5]
    
    stats = {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_views': total_views,
        'total_comments': total_comments,
        'approved_comments': approved_comments,
        'pending_comments': Comment.objects.filter(is_approved=False).count(),
        'recent_posts': PostListSerializer(recent_posts, many=True).data,
        'popular_posts': PostListSerializer(popular_posts, many=True).data,
        'pending_comments': CommentSerializer(pending_comments, many=True).data,
    }
    
    return Response(stats)
