from lib2to3.fixes.fix_input import context

from forms.user_create_form import UserCreationForm
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.models import Post, Comment, Follow, User, Profile, Category, CategoryPost
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

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.all()
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


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    posts = Post.objects.filter(user=user)

    return render(request, 'profile/profile.html', {'user': user, 'profile': profile, 'posts': posts})
