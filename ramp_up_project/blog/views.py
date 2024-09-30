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
            post = form.save(commit=False)  # Sla het formulier op, maar nog niet in de database
            post.user = request.user  # Vul de user ForeignKey met de ingelogde gebruiker
            post.save()  # Sla nu de post op
            return redirect('home')  # Redirect naar bijvoorbeeld de homepagina
    else:
        form = PostForm()

    return render(request, 'create_post.html', {'form': form})


def edit_post_view(request, post_id):

    if request.method == 'PUT':
        form = PostForm(request.PUT, request.FILES)  # Vul het formulier met de bestaande post
        if form.is_valid():
            post = form.save(commit=False)  # Sla het formulier op, maar nog niet in de database
            post.user = request.user  # Vul de user ForeignKey met de ingelogde gebruiker
            post.save()  # Sla nu de post op
            return redirect('home')  # Redirect naar bijvoorbeeld de homepagina
    else:
        form = PostForm()  # Vul het formulier met de bestaande post

    return render(request, 'create_post.html', {'form': form})