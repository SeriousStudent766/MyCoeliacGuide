from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings  
from django.conf.urls.static import static  
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'), 
    path('SignUp/', views.SignUp, name='SignUp'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    path('MyGuideHome/', views.MyGuideHome, name='MyGuideHome'),
    path('logout/', views.logout_view, name='logout'),
    path('community/', views.community, name='community'),
    path('health_profile/', views.health_profile, name='health_profile'),
    path('glutenExposure/', views.glutenExposure, name='glutenExposure'),

    path('recipes/', views.recipe_page, name='recipes'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/<int:recipe_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('recipes/favorites/', views.favorites_list, name='favorites_list'),

    path('dietary-intake/', views.dietary_intake, name='dietary_intake'),
    path('dietary-history/', views.dietary_history, name='dietary_history'),
    path('dietary-history/<str:date>/', views.view_day_logs, name='view_day_logs'),
   


    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    




]


if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
