from django import forms
from blog.models import Post, Category


class PostForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = Post
        fields = ['image', 'caption', 'categories']  # We leave 'user' out because it's set automatically.
        widgets = {
            'caption': forms.Textarea(attrs={
                'placeholder': 'Write your caption here...',
                'rows': 4,
                'class': 'form-control'  # Adding Bootstrap class for styling (if applicable)
            }),
        }
        labels = {
            'image': 'Post Image',
            'caption': 'Caption',
            'category': 'Category',
        }

    def clean_caption(self):
        caption = self.cleaned_data.get('caption')
        if len(caption) > 500:  # Example validation: maximum caption length
            raise forms.ValidationError("Caption cannot exceed 500 characters.")
        return caption
