from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Public URLs (No Authentication Required)
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('posts/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('stats/', views.blog_stats, name='blog_stats'),
    path('posts/<slug:post_slug>/comments/', views.add_comment, name='add_comment'),
    
    # Admin URLs (Authentication Required)
    path('admin/posts/', views.AdminPostListCreateView.as_view(), name='admin_post_list_create'),
    path('admin/posts/<int:pk>/', views.AdminPostDetailView.as_view(), name='admin_post_detail'),
    path('admin/categories/', views.AdminCategoryListCreateView.as_view(), name='admin_category_list_create'),
    path('admin/tags/', views.AdminTagListCreateView.as_view(), name='admin_tag_list_create'),
    path('admin/comments/', views.AdminCommentListView.as_view(), name='admin_comment_list'),
    path('admin/comments/<int:comment_id>/approve/', views.approve_comment, name='approve_comment'),
    path('admin/stats/', views.admin_blog_stats, name='admin_blog_stats'),
]



