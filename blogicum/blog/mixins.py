from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        post_id = self.kwargs.get('post_id')
        return redirect('blog:post_detail', post_id)
