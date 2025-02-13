from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    CreateView, DetailView, ListView, UpdateView
)
from django.urls import reverse

from .models import Post, Category, Comment
from .mixins import OnlyAuthorMixin
from .forms import PostForm, UserProfileForm, CommentForm
from .query_utils import get_optimized_post_queryset

User = get_user_model()
MAX_POSTS = settings.MAX_POSTS


class IndexView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = MAX_POSTS

    def get_queryset(self):
        return get_optimized_post_queryset(
            apply_filters=True,
            apply_annotation=True
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        user = (
            self.request.user if self.request.user.is_authenticated else None
        )
        return get_optimized_post_queryset(
            apply_filters=True,
            apply_annotation=True,
            user=user  # Передаем пользователя только если он авторизован
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.get_object().comments.select_related(
            'author').all()
        return context


class CategoryPostView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = MAX_POSTS

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        category = CategoryPostView.get_category(self)
        return get_optimized_post_queryset(
            manager=category.posts,
            apply_filters=True,
            apply_annotation=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.object.id}
        )


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Проверяем, что пользователь является автором поста
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(instance=post)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', request.user.username)

    return render(request, 'blog/create.html', context={'form': form})


class ProfileView(ListView):
    template_name = 'blog/profile.html'
    context_object_name = 'post_list'
    paginate_by = MAX_POSTS

    def get_username(self):
        return self.kwargs.get('username')

    def get_queryset(self):
        username = ProfileView.get_username(self)
        user = get_object_or_404(User, username=username)
        if self.request.user == user:
            # Автор видит все свои посты, включая снятые с публикации
            return get_optimized_post_queryset(manager=user.posts,
                                               apply_filters=False,
                                               apply_annotation=True)
        else:
            # Другие пользователи видят только опубликованные посты
            return get_optimized_post_queryset(
                manager=user.posts,
                apply_filters=True,
                apply_annotation=True
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = ProfileView.get_username(self)
        context['profile'] = get_object_or_404(User, username=username)
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self, queryset=None):

        post_id = self.kwargs.get('post_id')
        comment_id = self.kwargs.get('comment_id')

        return get_object_or_404(Comment, id=comment_id, post_id=post_id)

    def get_success_url(self):
        comment = self.get_object()
        return reverse('blog:post_detail',
                       kwargs={'post_id': comment.post.id})


@login_required
def comment_delete(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'post': comment.post,
        'comment': comment,
    })
