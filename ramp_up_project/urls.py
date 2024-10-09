from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog.views import (
    PostDetailView,
    SignUpView,
    ForYouPageView,
    PostCreationView,
    ListPostsView,
    PostUpdateView,
    ProfileDetailView,
    ProfileUpdateView,
    Unfollow,
    Follow,
    LikePostView,
)

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    path('admin_tools_stats/', include('admin_tools_stats.urls')),

    # Authentication views
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),

    # Main views
    path('', ForYouPageView.as_view(), name='foryoupage'),  # For You page
    path('foryoupage/', ForYouPageView.as_view(), name='foryoupage_redirect'),  # Redirect to For You page

    # Post management
    path('create_post/', PostCreationView.as_view(), name='create_post'),  # Create a post
    path('posts/', ListPostsView.as_view(), name='list_posts'),  # List all posts
    path('post/<uuid:id>/', PostDetailView.as_view(), name='post_detail'),
    path('update_post/<uuid:pk>/', PostUpdateView.as_view(), name='update_post'),  # Update a post

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
