from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('create-key/', views.create_key_view, name='create_key'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('history/', views.history_view, name='history'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('profile/', views.profile_view, name='profile'),
    path('task/<int:task_id>/toggle/', views.toggle_task_view, name='toggle_task'),
    path('task/<int:task_id>/delete/', views.delete_task_view, name='delete_task'),
]
