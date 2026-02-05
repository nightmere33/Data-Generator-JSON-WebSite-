from django.urls import path
from . import views  # Import the module, not specific classes

urlpatterns = [
    path('', views.index, name='index'),
    path('form/', views.form_view, name='form'),
    path('preview/', views.preview_view, name='preview'),
    path('download-json/', views.download_json, name='download_json'),
    path('success/', views.success_view, name='success'),
]