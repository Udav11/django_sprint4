from django.urls import path, include

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('category/<slug:category_slug>/',
         views.CategoryPostView.as_view(), name='category_posts'),
    path('posts/<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('profile/edit/', views.EditProfile.as_view(), name='edit_profile'),
    path('profile/<username>/', views.Profile.as_view(), name='profile'),
    

]
