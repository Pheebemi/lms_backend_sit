from django.contrib.admin.views.main import ChangeList
from django.db.models import Count, Sum
from django.utils.html import format_html
from django.urls import reverse
from .models import Post, Category, Tag, Comment


class BlogStatsChangeList(ChangeList):
    """Custom ChangeList to add blog statistics to admin dashboard"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add blog statistics
        context['blog_stats'] = {
            'total_posts': Post.objects.count(),
            'published_posts': Post.objects.filter(status='published').count(),
            'draft_posts': Post.objects.filter(status='draft').count(),
            'total_views': Post.objects.aggregate(total_views=Sum('views'))['total_views'] or 0,
            'total_comments': Comment.objects.count(),
            'pending_comments': Comment.objects.filter(is_approved=False).count(),
            'categories': Category.objects.count(),
            'tags': Tag.objects.count(),
        }
        
        return context


def blog_stats_widget(request):
    """Custom widget to display blog statistics in admin dashboard"""
    from django.db.models import Sum
    
    stats = {
        'total_posts': Post.objects.count(),
        'published_posts': Post.objects.filter(status='published').count(),
        'draft_posts': Post.objects.filter(status='draft').count(),
        'total_views': Post.objects.aggregate(total_views=Sum('views'))['total_views'] or 0,
        'total_comments': Comment.objects.count(),
        'pending_comments': Comment.objects.filter(is_approved=False).count(),
    }
    
    return format_html(
        '''
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h3 style="margin: 0 0 10px 0; color: #333;">📊 Blog Statistics</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                <div style="text-align: center; padding: 10px; background: white; border-radius: 3px;">
                    <div style="font-size: 24px; font-weight: bold; color: #007cba;">{total_posts}</div>
                    <div style="font-size: 12px; color: #666;">Total Posts</div>
                </div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 3px;">
                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">{published_posts}</div>
                    <div style="font-size: 12px; color: #666;">Published</div>
                </div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 3px;">
                    <div style="font-size: 24px; font-weight: bold; color: #ffc107;">{draft_posts}</div>
                    <div style="font-size: 12px; color: #666;">Drafts</div>
                </div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 3px;">
                    <div style="font-size: 24px; font-weight: bold; color: #17a2b8;">{total_views}</div>
                    <div style="font-size: 12px; color: #666;">Total Views</div>
                </div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 3px;">
                    <div style="font-size: 24px; font-weight: bold; color: #6f42c1;">{total_comments}</div>
                    <div style="font-size: 12px; color: #666;">Comments</div>
                </div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 3px;">
                    <div style="font-size: 24px; font-weight: bold; color: #dc3545;">{pending_comments}</div>
                    <div style="font-size: 12px; color: #666;">Pending</div>
                </div>
            </div>
        </div>
        ''',
        **stats
    )



