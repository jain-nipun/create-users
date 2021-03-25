from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home_view, name='home_page'),
    path('signup/', views.signup_view, name='signup_page'),
    path('signin/', views.signin_view, name='signin_page'),
    path('signout/', LogoutView.as_view(), name='signout_page'),
    path('dashboard/', views.dashboard_view, name='dashboard_page'),
    path('api/my-notes/', views.my_notes_api, name='my_notes_api'),
    path('api/add-notes/', views.add_notes_api, name='add_notes_api'),
    path('api/edit-notes/<int:id>/', views.edit_notes_api, name='edit_notes_api'),
    path('api/delete-notes/<int:id>/', views.delete_notes_api, name='delete_notes_api'),
    path('api/get-users/', views.get_users_api, name='get_users_api'),
]