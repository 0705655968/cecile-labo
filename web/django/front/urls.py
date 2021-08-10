from django.urls import path
from . import views
 
app_name = 'front'
urlpatterns = [
    path('viewer/<int:pk>/', views.degitalcatalog, name='degitalcatalog'),
    path('viewer', views.viewer, name="viewer"),
    path('design', views.design, name="design"),
    path('home', views.home, name="home"),
    path('catalog', views.catalog, name="catalog"),
    path('similar', views.similar, name="similar"),
    path('news', views.news, name="news"),
    path('image', views.image, name="image"),
    path('settings', views.settings, name="settings"),
]