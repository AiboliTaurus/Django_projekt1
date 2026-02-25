# blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Список статей
    path('', views.BlogPostListView.as_view(), name='blog_list'),

    # Детальная страница статьи
    path('<int:pk>/', views.BlogPostDetailView.as_view(), name='blog_detail'),

    # Создание статьи
    path('create/', views.BlogPostCreateView.as_view(), name='blog_create'),

    # Редактирование статьи
    path('<int:pk>/edit/', views.BlogPostUpdateView.as_view(), name='blog_edit'),

    # Удаление статьи
    path('<int:pk>/delete/', views.BlogPostDeleteView.as_view(), name='blog_delete'),
]
