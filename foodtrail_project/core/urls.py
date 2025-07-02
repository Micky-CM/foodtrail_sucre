from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('explore/', views.home, name='home'),
    path('establishment/<int:establishment_id>/', views.establishment_detail, name='establishment_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)