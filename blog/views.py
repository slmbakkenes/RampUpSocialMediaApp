from msilib.schema import ListView

from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from blog.models import Post, Comment, Follow

from django.views.generic import CreateView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from blog.models import Post
from forms.post_form import PostForm

# Create your views here.
class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class ForYouPageView(ListView):
    template_name = "forYouPage.html"
    paginate_by = 15
    model = Post

    def get_queryset(self):
        queryset = super().get_queryset()
        path = self.request.path

        if "/foryoupage/" == path:
            following = Follow.objects.filter(follower=self.request.user).values_list('following', flat=True)
            queryset = queryset.filter(user__in=following)

        return queryset.order_by("-created_at")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.all()
        return context


class PostCreationView(CreateView):
    form_class = UserCreationForm
    template_name = "Post/create_post.html"

    @login_required
    def create_post_view(request):
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user  # Koppel de post aan de ingelogde gebruiker
                post.save()
                return redirect('profile', user_id=request.user.id)  # Redirect naar de profielpagina
        else:
            form = PostForm()
        return render(request, 'create_post.html', {'form': form})

def list_posts_view(request):
    posts = Post.objects.all()  # Haal alle posts op
    return render(request, 'list_posts.html', {'posts': posts})

def update_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)  # Haal de post op
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)  # Geef het bestaande object door
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=request.user.id)  # Redirect naar de profielpagina
    else:
        form = PostForm(instance=post)  # Vul het formulier met de huidige gegevens van de post
    return render(request, 'update_post.html', {'form': form, 'post': post})

def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()  # Verwijder de post
        return redirect('profile', user_id=request.user.id)  # Redirect naar de profielpagina
    return render(request, 'confirm_delete.html', {'post': post})