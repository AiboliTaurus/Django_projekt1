# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('', views.home, name='home'),
#     path('contacts/', views.contacts, name='contacts'),
#     path('product/<int:pk>/', views.product_detail, name='product_detail'),
#     path('product/create/', views.product_create, name='product_create'),  # НОВЫЙ URL
# ]

# catalog/urls.py - ЗАМЕНЯЕМ на новую версию
from django.urls import path
from . import views

app_name = 'catalog'  # Добавляем namespace для приложения

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    # НОВЫЕ МАРШРУТЫ:
    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
]
