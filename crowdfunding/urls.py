from django.urls import path
from crowdfunding import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.home_view, name='home'),
    path('create-new-user/', views.create_new_user_view, name='create_new_user'),
    path('create-new-user/ok/', views.create_new_user_ok_view, name='create_new_user_ok'),
    path('login/', LoginView.as_view(template_name= 'login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page= 'home'), {}, name='logout'),
    path('create-new-project/', views.create_new_project_view, name='create_new_project'),
    path('create-new-user/ok2/', views.create_new_user_ok2_view, name='create_new_user_ok2'),
    path('project/', views.all_project_view, name='project'),
    path('category/<int:pk>', views.getCategory, name='category'),
    path('payment/<int:pk>', views.payment_view, name='payment'),
    path('project/<int:pk>', views.project_detail_view, name='project-detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('search/', views.search_view, name='search'),
    path('myproject/', views.my_project_view, name='my-project'),
    path('charge/<int:pk>', views.charge, name="charge"),
    path('success/<str:args>', views.successMsg, name="success"),
    path('mydonate/', views.my_donate_view, name='my-donate'),
]