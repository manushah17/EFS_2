
from django.contrib import admin
from django.urls import path, include
from portfolio.views import login_view, logout_view, register_view

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('', include('portfolio.urls')),


]
