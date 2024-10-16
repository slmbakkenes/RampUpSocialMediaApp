"""
URL configuration for ramp_up_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog.views import (
    SignUpView,
    ForYouPageView,
    PostCreationView,
    ListPostsView,
    PostUpdateView,
    PostDeleteView,
    ProfileDetailView,
    ProfileUpdateView,
    Unfollow,
    Follow,
    LikePostView,
    ReportPostView,
    CommentDeleteView,
    CommentCreationView,
    EditCommentView
)

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    path('admin_tools_stats/', include('admin_tools_stats.urls')),

    # Authentication views
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),

    # Main views
    path('', ForYouPageView.as_view(), name='foryoupage'),
    path('foryoupage/', ForYouPageView.as_view(), name='foryoupage_redirect'),

    # Post management
    path('create_post/', PostCreationView.as_view(), name='create_post'),  # Create a post
    path('posts/', ListPostsView.as_view(), name='list_posts'),  # List all posts
    path('update_post/<uuid:pk>/', PostUpdateView.as_view(), name='update_post'),  # Update a post
    path('post/<uuid:post_id>/report/', ReportPostView.as_view(), name='report_post'),
    path('post/delete/<uuid:pk>/', PostDeleteView.as_view(), name='post_delete'), # Delete a post

    # Comment management
    path('comment/delete/<uuid:pk>/', CommentDeleteView.as_view(), name='comment_delete'),
    path('post/<uuid:pk>/comment/add/', CommentCreationView.as_view(), name='add_comment'),
    path('comment/<uuid:pk>/edit/', EditCommentView.as_view(), name='comment_edit'),

    # Profile view
    path('profile/<str:username>/', ProfileDetailView.as_view(), name='profile'),
    path('profile/<str:username>/update/', ProfileUpdateView.as_view(), name='profile_update'),

    # Followers
    path('follow/<str:username>/', Follow.as_view(), name='follow'),
    path('unfollow/<str:username>/', Unfollow.as_view(), name='unfollow'),

    # Like Post URL using the class-based view
    path('post/<uuid:post_id>/like/', LikePostView.as_view(), name='like_post'),
    path('ajax/like/', LikePostView.as_view(), name='ajax_like_post'),  # AJAX version

    # Default authentication URLs (includes password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

