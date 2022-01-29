from django import forms

from .models import Post
from .validators import clean_text


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        widgets = {'text': forms.Textarea(attrs={'cols': 103, 'rows': 20})}
        labels = {'text': 'Введите текст нового поста',
                  'group': 'Выберите группу, '
                           'к которой будет относиться ваш пост'}
        validators = {'text': clean_text}
