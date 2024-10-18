from django import forms
from blog.models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']  # Het enige veld dat we willen dat de gebruiker invult
        widgets = {
            'comment': forms.Textarea(attrs={
                'placeholder': 'Write your comment here...',  # Placeholder voor het commentaar
                'rows': 4,  # Aantal rijen in de textarea
                'class': 'form-control',  # Bootstrap class voor styling
            }),
        }
        labels = {
            'comment': 'Comment',  # Label voor het commentaar veld
        }

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if len(comment) > 300:  # Voorbeeldvalidatie: maximum lengte van het commentaar
            raise forms.ValidationError("Comment cannot exceed 300 characters.")
        return comment