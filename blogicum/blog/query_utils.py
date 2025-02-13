from django.db.models import Count, Q
from django.utils import timezone

from .models import Post


def get_optimized_post_queryset(manager=Post.objects,
                                apply_filters=True,
                                apply_annotation=True,
                                user=None):
    queryset = manager.select_related('author', 'category', 'location')

    if apply_filters:
        if user is not None:
            queryset = queryset.filter(
                (Q(is_published=True) | Q(author=user)) & Q(
                    (Q(category__is_published=True) | Q(author=user))
                ))
        else:
            queryset = queryset.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )

    if apply_annotation:
        queryset = queryset.annotate(
            comment_count=Count('comments')).order_by('-pub_date')

    return queryset
