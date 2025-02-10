from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Post, Comment


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }
        fields = ['title', 'text', 'pub_date', 'category', 'image', 'location']

    def clean_pub_date(self):
        pub_date = self.cleaned_data['pub_date']
        if pub_date < timezone.now():
            raise forms.ValidationError(
                'Дата публикации не может быть в прошлом.')
        return pub_date


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
