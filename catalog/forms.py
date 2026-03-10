from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category
import os


class ProductForm(forms.ModelForm):
    """Форма для добавления и редактирования товара с кастомной валидацией"""

    # Константа со списком запрещённых слов (ЗАДАНИЕ 1)
    FORBIDDEN_WORDS = [
        'казино', 'криптовалюта', 'крипта', 'биржа',
        'дешево', 'бесплатно', 'обман', 'полиция', 'радар'
    ]

    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price']
        # Базовые виджеты (будут дополнены в __init__)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Введите название товара'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Введите описание товара'}),
            'price': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }
        labels = {
            'name': 'Название товара',
            'description': 'Описание',
            'image': 'Изображение',
            'category': 'Категория',
            'price': 'Цена (₽)',
        }
        help_texts = {
            'price': 'Введите цену в рублях',
        }

    def __init__(self, *args, **kwargs):
        """ЗАДАНИЕ 3: Стилизация формы через __init__"""
        super().__init__(*args, **kwargs)

        # Словарь с классами Bootstrap для разных типов полей
        bootstrap_classes = {
            'text': 'form-control',
            'textarea': 'form-control',
            'number': 'form-control',
            'select': 'form-select',
            'file': 'form-control',
            'checkbox': 'form-check-input',
        }

        # Применяем стилизацию ко всем полям
        for field_name, field in self.fields.items():
            # Определяем тип поля и применяем соответствующий класс
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

            # Добавляем плейсхолдеры, если их нет
            if not field.widget.attrs.get('placeholder') and field_name != 'image':
                field.widget.attrs['placeholder'] = f'Введите {field.label.lower()}'

        # Специальная обработка для поля image
        self.fields['image'].widget.attrs.update({
            'accept': 'image/*'  # Ограничиваем выбор только изображениями
        })

    def clean_name(self):
        """ЗАДАНИЕ 1: Валидация поля name на запрещённые слова"""
        name = self.cleaned_data.get('name')
        if name:
            name_lower = name.lower()
            for word in self.FORBIDDEN_WORDS:
                if word in name_lower:
                    raise ValidationError(
                        f'Название не может содержать слово "{word}". '
                        f'Пожалуйста, уберите его из названия.'
                    )
        return name

    def clean_description(self):
        """ЗАДАНИЕ 1: Валидация поля description на запрещённые слова"""
        description = self.cleaned_data.get('description')
        if description:
            desc_lower = description.lower()
            for word in self.FORBIDDEN_WORDS:
                if word in desc_lower:
                    raise ValidationError(
                        f'Описание не может содержать слово "{word}". '
                        f'Пожалуйста, уберите его из описания.'
                    )
        return description

    def clean_price(self):
        """ЗАДАНИЕ 2: Валидация поля price (неотрицательная цена)"""
        price = self.cleaned_data.get('price')
        if price is not None:
            if price < 0:
                raise ValidationError(
                    'Цена не может быть отрицательной. '
                    'Пожалуйста, укажите корректную цену.'
                )
            if price == 0:
                raise ValidationError(
                    'Цена не может быть равной нулю. '
                    'Пожалуйста, укажите цену больше 0.'
                )
        return price

    # ДОПОЛНИТЕЛЬНОЕ ЗАДАНИЕ: Валидация изображения
    def clean_image(self):
        """Доп. задание: Валидация формата и размера изображения"""
        image = self.cleaned_data.get('image')

        # Если изображение не загружено (необязательное поле) - пропускаем валидацию
        if not image:
            return image

        # Если это существующий файл (при редактировании без замены) - пропускаем валидацию
        if hasattr(image, 'name') and not hasattr(image, 'content_type'):
            # Это существующий файл из базы данных, а не новый загруженный
            return image

        # Проверка формата файла (только для новых загруженных файлов)
        valid_formats = ['image/jpeg', 'image/png', 'image/jpg']
        if hasattr(image, 'content_type') and image.content_type not in valid_formats:
            raise ValidationError(
                'Неподдерживаемый формат изображения. '
                'Пожалуйста, загрузите файл в формате JPEG или PNG.'
            )

        # Проверка размера файла (макс. 5 МБ) - только для новых файлов
        max_size = 5 * 1024 * 1024  # 5 МБ в байтах
        if hasattr(image, 'size') and image.size > max_size:
            size_mb = image.size / (1024 * 1024)
            raise ValidationError(
                f'Размер файла слишком большой ({size_mb:.1f} МБ). '
                f'Максимальный размер: 5 МБ.'
            )

        # Проверка расширения файла (дополнительная защита) - только для новых файлов
        if hasattr(image, 'name'):
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                raise ValidationError(
                    'Неподдерживаемое расширение файла. '
                    'Используйте .jpg, .jpeg или .png.'
                )

        return image
