
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:profile>", views.user_profile, name="user_profile"),
    path("following", views.following_page, name="following"),

    # API Routes
    path("create_post", views.create_post, name="create_post"),
    path("load_posts", views.load_posts, name="load_posts"),
    path("load_posts_following_page", views.load_posts_following_page, name="load_posts_following_page"),
    path("get_users_posts/<str:profile>", views.get_profiles_posts, name="get_profiles_posts"),
    path("get_follow_data/<str:profile>", views.get_follow_data, name="get_follow_data"),
    path("update_post/<int:post_id>", views.update_post, name="update_post"),
    path("like_post/<int:post_id>", views.like_post, name="like_post")
]
