from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount, Comment, Category, CategoryPost, Follow

# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'profile_img')

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'caption', 'created_at', 'no_of_likes')
    search_fields = ('caption',)

class LikePostAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'user')

class FollowersCountAdmin(admin.ModelAdmin):
    list_display = ('follower', 'user')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'user', 'comment', 'comment_date')
    search_fields = ('comment',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)

class CategoryPostAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'post_id')

class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(LikePost, LikePostAdmin)
admin.site.register(FollowersCount, FollowersCountAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryPost, CategoryPostAdmin)
admin.site.register(Follow, FollowAdmin)
