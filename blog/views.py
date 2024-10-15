from blog.forms import ProfileForm
from forms.comment_form import CommentForm
from forms.user_create_form import UserCreationForm
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, DeleteView, DetailView
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
class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'post/post_detail.html'  # Dit is de template waarin je de bevestiging voor verwijderen toont.

    def get_success_url(self):
        # Redirect naar de detailpagina van de post na succesvolle verwijdering
        return reverse_lazy('post_detail', kwargs={'post_id': self.object.post.id})

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            return HttpResponseForbidden()  # Voorkom ongeautoriseerde verwijderingen
        return super().dispatch(request, *args, **kwargs)

class CommentCreationView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'post/post_detail.html'  # Maak deze template aan voor het toevoegen van opmerkingen

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])  # Verkrijg de post
        form.instance.user = self.request.user  # Koppel de gebruiker aan de opmerking
        form.instance.post = post  # Koppel de opmerking aan de post
        response = super().form_valid(form)  # Verwerk het formulier en sla de opmerking op
        return response  # Geef de response terug na succesvolle validatie

    def get_success_url(self):
        # Redirect naar de detailpagina van de post na succesvol toevoegen van een commentaar
        return reverse_lazy('post_detail', kwargs={'post_id': self.object.post.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs['post_id'])  # Verkrijg de post om deze in de context te kunnen gebruiken
        return context

class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'post/post_detail.html'  # Hier stellen we de juiste template in voor bewerken

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            return HttpResponseForbidden()  # Voorkom ongeautoriseerde bewerkingen
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'post_id': self.object.post.id})
