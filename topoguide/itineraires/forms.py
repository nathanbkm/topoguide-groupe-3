from django import forms

from .models import Comment

class CommentForm(forms.ModelForm):
    """
    A form based on models.Comment with description and moderation status
    """
    class Meta:
        model = Comment
        fields = ['description', 'mod_status']
        
        
class ImageForm(forms.Form):
    """
    A form to upload multiple images for a single trip
    """
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
