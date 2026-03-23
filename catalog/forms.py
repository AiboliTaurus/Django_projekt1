# catalog/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category
import os


class ProductForm(forms.ModelForm):
    """Форма для добавления и редактирования товара"""

    FORBIDDEN_WORDS = [
        'казино', 'криптовалюта', 'крипта', 'биржа',
        'дешево', 'бесплатно', 'обман', 'полиция', 'радар'
    ]

    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price', 'is_published']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Введите название товара'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Введите описание товара'}),
            'price': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Название товара',
            'description': 'Описание',
            'image': 'Изображение',
            'category': 'Категория',
            'price': 'Цена (₽)',
            'is_published': 'Опубликовать товар',
        }
        help_texts = {
            'price': 'Введите цену в рублях',
            'is_published': 'Отметьте, чтобы опубликовать товар',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        bootstrap_classes = {
            'text': 'form-control',
            'textarea': 'form-control',
            'number': 'form-control',
            'select': 'form-select',
            'file': 'form-control',
            'checkbox': 'form-check-input',
        }

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['class'] = bootstrap_classes['text']
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = bootstrap_classes['textarea']
                field.widget.attrs['rows'] = 4
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs['class'] = bootstrap_classes['number']
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = bootstrap_classes['select']
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = bootstrap_classes['file']
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = bootstrap_classes['checkbox']

            if not field.widget.attrs.get('placeholder') and field_name not in ['image', 'is_published']:
                field.widget.attrs['placeholder'] = f'Введите {field.label.lower()}'

        self.fields['image'].widget.attrs.update({
            'accept': 'image/*'
        })

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name_lower = name.lower()
            for word in self.FORBIDDEN_WORDS:
                if word in name_lower:
                    raise ValidationError(
                        f'Название не может содержать слово "{word}".'
                    )
        return name

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            desc_lower = description.lower()
            for word in self.FORBIDDEN_WORDS:
                if word in desc_lower:
                    raise ValidationError(
                        f'Описание не может содержать слово "{word}".'
                    )
        return description

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None:
            if price < 0:
                raise ValidationError('Цена не может быть отрицательной.')
            if price == 0:
                raise ValidationError('Цена не может быть равной нулю.')
        return price

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        if hasattr(image, 'name') and not hasattr(image, 'content_type'):
            return image

        valid_formats = ['image/jpeg', 'image/png', 'image/jpg']
        if hasattr(image, 'content_type') and image.content_type not in valid_formats:
            raise ValidationError('Неподдерживаемый формат изображения. Используйте JPEG или PNG.')

        max_size = 5 * 1024 * 1024
        if hasattr(image, 'size') and image.size > max_size:
            size_mb = image.size / (1024 * 1024)
            raise ValidationError(f'Размер файла слишком большой ({size_mb:.1f} МБ). Максимум 5 МБ.')

        if hasattr(image, 'name'):
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                raise ValidationError('Неподдерживаемое расширение файла. Используйте .jpg, .jpeg или .png.')

        return image
