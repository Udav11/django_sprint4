from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from blog.forms import PostForm, UserProfileForm, CommentForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.utils import timezone
from django.urls import reverse_lazy
from blog.models import Post, Category, Comment

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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем комментарии для каждого поста
        context['post_list'] = [
            {
                'post': post,
                'comment_count': post.comments.count()  # Количество комментариев
            }
            for post in context['post_list']
        ]
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


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


class PostUpdateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        post = self.get_object()
        return reverse_lazy('blog:post_detail', post_id=post.id)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.object.id})


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

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        if self.request.user == user:
            return Post.objects.filter(author=user)
        return Post.objects.filter(
            author=user,
            is_published=True,
            pub_date__lte=timezone.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        context['profile'] = get_object_or_404(User, username=username)
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


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
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        comment = self.get_object()
        return reverse_lazy('blog:post_detail', post_id=comment.post.id)

    def get_success_url(self):
        comment = self.get_object()
        return reverse_lazy('blog:post_detail', kwargs={'post_id': comment.post.id})


@login_required
def comment_delete(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Проверяем, что пользователь является автором комментария
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'post': comment.post,
        'comment': comment,
        'form': CommentForm(), }
    )



