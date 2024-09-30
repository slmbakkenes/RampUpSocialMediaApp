from django import forms
from blog.models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'caption']  # We laten 'user' weg omdat deze automatisch wordt ingesteld.