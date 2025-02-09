from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from blog.forms import PostForm, UserProfileForm
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.utils import timezone
from django.urls import reverse_lazy
from blog.models import Post, Category

User = get_user_model()
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


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class Profile(ListView):
    template_name = 'blog/profile.html'
    model = User
    context_object_name = 'page_obj'
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(self.model, username=username)
        return Post.objects.filter(author=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        context['profile'] = get_object_or_404(User, username=username)
        return context


class EditProfile(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})
