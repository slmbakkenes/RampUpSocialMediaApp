# views.py
from blog import models
from blog.forms import ProfileForm
from forms.user_create_form import UserCreationForm
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.models import Post, Comment, Follow, User, Profile, Category, CategoryPost, LikePost
from forms.post_form import PostForm


# Home view that requires login
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    login_url = 'login'  # Redirect to login if not authenticated


# Sign-up view for creating a new user
class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


# View for the "For You" page showing posts from followed users
class ForYouPageView(LoginRequiredMixin, ListView):
    template_name = "index.html"
    paginate_by = 15
    model = Post

    def get_queryset(self):
        queryset = super().get_queryset()
        path = self.request.path

        if "/foryoupage/" == path:
            following = Follow.objects.filter(follower=self.request.user).values_list('following', flat=True)
            queryset = queryset.filter(user__in=following)

        categories = self.request.GET.getlist('categories')
        if categories:
            queryset = queryset.filter(categorypost__category__id__in=categories).distinct()

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.all()
        context['categoryPosts'] = CategoryPost.objects.all()
        context['categories'] = Category.objects.all()
        context['checked'] = self.request.GET.getlist('categories')
        liked_posts = LikePost.objects.filter(user=self.request.user).values_list('post_id', flat=True)
        context['liked_posts'] = liked_posts
        return context


# View for creating a new post
class PostCreationView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = "Post/create_post.html"

    def form_valid(self, form):
        form.instance.user = self.request.user  # Associate the post with the logged-in user
        response = super().form_valid(form)
        categories = form.cleaned_data.get('categories')
        for category in categories:
            CategoryPost.objects.create(post=self.object, category=category)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_success_url(self):
        # Redirect to the user's profile using the username
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})


# View for listing all posts
class ListPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'list_posts.html'
    paginate_by = 15  # You can adjust this as needed


# View for updating a post
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'update_post.html'

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'user_id': self.request.user.id})


# View for deleting a post
@login_required
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'user_id': self.request.user.id})

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.user != request.user:
            return HttpResponseForbidden()  # Prevent unauthorized deletions
        return super().dispatch(request, *args, **kwargs)


@login_required
def like_post(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        like = LikePost.objects.filter(post=post, user=request.user).first()
        liked = False

        if like:
            like.delete()
            post.no_of_likes -= 1
            post.save()
        else:
            new_like = LikePost(post=post, user=request.user)
            new_like.save()
            post.no_of_likes += 1
            post.save()
            liked = True

        return JsonResponse({
            'liked': liked,
            'no_of_likes': post.no_of_likes,
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'profile/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['profile'] = get_object_or_404(Profile, user=user)
        context['posts'] = Post.objects.filter(user=user)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profile/profile_update.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return get_object_or_404(Profile, user=user)

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.save()
        return redirect('profile', username=self.kwargs['username'])
