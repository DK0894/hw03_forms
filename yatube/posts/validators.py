from django import forms


def clean_text(self):
    text = self.cleaned_data['text']
    if text == '':
        raise forms.ValidationError('Не заполнено поле "Текст поста"!')
    return text
