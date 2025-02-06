from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'required': True}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'required': True}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=False)