from django import forms
from .models import Comment,Classify,Recipe

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '',  # Để trống nếu bạn không muốn hiển thị nhãn
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Nhập Bình Luận...'}),
        }


