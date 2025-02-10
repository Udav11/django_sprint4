from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from blog.forms import PostForm, UserProfileForm
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.utils import timezone
from django.urls import reverse_lazy
from blog.models import Post, Category

User = get_user_model()
Now = timezone.now()
MAX_POSTS = 10


class IndexView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = MAX_POSTS

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True, 
            category__is_published=True, 
            pub_date__lt=Now
            )


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    model = Post

    def get_object(self, queryset=None):
        post_id = self.kwargs['post_id']
        return get_object_or_404(Post, id=post_id)

class CategoryPostView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = MAX_POSTS

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']

        return Post.objects.filter(
            category__slug=category_slug,
            is_published=True
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        context['category'] = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        return context


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
    context_object_name = 'post_list'
    paginate_by = MAX_POSTS

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

