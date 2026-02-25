# blog/forms.py
from django import forms
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    """Форма для создания и редактирования блоговой записи"""

    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'preview', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок статьи'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Введите содержимое статьи'
            }),
            'preview': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержимое',
            'preview': 'Превью (изображение)',
            'is_published': 'Опубликовать статью',
        }
