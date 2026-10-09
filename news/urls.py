from django.urls import path
from .views import HomeView, CategoryDetailView, ArticleDetailView

app_name = 'news'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('categoria/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('articulo/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
]