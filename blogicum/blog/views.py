from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from blog.models import Post, Category

Now = timezone.now()
MAX_POSTS = 5


def get_objects():
    return Post.objects.select_related(
        'author', 'category', 'location'
    ).filter(
        pub_date__lt=Now, is_published=True, category__is_published=True
    )


def index(request):
    post_list = get_objects()[:MAX_POSTS]
    return render(request, 'blog/index.html', {'post_list': post_list})


def post_detail(request, post_id):
    post_list = get_object_or_404(
        get_objects(), id=post_id
    )
    return render(request, 'blog/detail.html', {'post': post_list})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects.values(),
        slug=category_slug,
        is_published=True
    )
    post_list = get_objects().filter(
        category__slug=category_slug,
    )
    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, 'blog/category.html', context)
