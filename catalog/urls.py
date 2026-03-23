# catalog/urls.py

from django.urls import path
from django.views.decorators.cache import cache_page
from . import views

app_name = 'catalog'

urlpatterns = [
    # ✅ Главная страница - кэш 15 минут
    path('', cache_page(60 * 15)(views.HomeView.as_view()), name='home'),

    # Контакты - без кэша (форма обратной связи)
    path('contacts/', views.ContactsView.as_view(), name='contacts'),

    # Детальная страница товара - кэш 10 минут (дополнительно к низкоуровневому)
    path('product/<int:pk>/', cache_page(60 * 10)(views.ProductDetailView.as_view()), name='product_detail'),

    # CRUD операции - без кэша (динамические)
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:pk>/unpublish/', views.ProductUnpublishView.as_view(), name='product_unpublish'),

    # Страница категории - кэш 5 минут
    path('category/<str:category_name>/', cache_page(60 * 5)(views.CategoryProductsView.as_view()),
         name='category_products'),
]
