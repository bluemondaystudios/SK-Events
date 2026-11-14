from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('news/<slug:slug>/', views.article_detail, name='article-detail'),
    path('category/<str:category>/', views.article_category, name='article-category'),
]
