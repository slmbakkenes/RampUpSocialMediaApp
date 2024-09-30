from msilib.schema import ListView

from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from forms.post_form import PostForm

# Create your views here.
class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

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