from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('form/', views.form_view, name='form'),
    path('preview/', views.preview_view, name='preview'),
    path('download-json/', views.download_json, name='download_json'),
    path('register/<uuid:token>/', views.register_with_invite, name='register_with_invite'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]