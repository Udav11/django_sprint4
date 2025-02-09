from django import forms
from django.contrib.auth.models import User

from .models import Post

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


    

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'