from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('desk_dashboard/', views.desk_dashboard, name='desk_dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('reports_and_prescriptions/', views.user_reports_and_prescriptions, name='user_reports_and_prescriptions'),  # New URL pattern

]
