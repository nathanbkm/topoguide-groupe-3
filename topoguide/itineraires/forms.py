from django import forms

from .models import Comment

class CommentForm(forms.ModelForm):
    """
    A form based on models.Comment with description and moderation status
    """
    class Meta:
        model = Comment
        fields = ['description', 'mod_status']
