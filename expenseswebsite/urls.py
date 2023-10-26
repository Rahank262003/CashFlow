from django.contrib import admin
from userincome import views
from django.urls import path, include


urlpatterns = [
    path('', include('expenses.urls')),
    path('authentication/', include('authentication.urls')),
    path('preferences/', include('userpreferences.urls')),
    path('income/', include('userincome.urls')),
    path('income_category_summary', views.income_category_summary, name='income_category_summary'),
    path('admin/', admin.site.urls),
]
