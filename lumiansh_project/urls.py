from django.contrib import admin
from django.urls import path, include  # Make sure 'include' is imported!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),  # This line tells Django to use your shop's URLs
]