from django.urls import path
from . import views

app_name = 'utils'

urlpatterns = [
    # Image upload views
    path('images/upload/', views.image_upload_view, name='image_upload'),
    path('images/upload/<str:image_type>/', views.image_upload_view, name='image_upload_type'),
    path('images/upload/<str:image_type>/<str:entity_type>/<int:entity_id>/', 
         views.image_upload_view, name='image_upload_entity'),
    
    # AJAX image upload
    path('api/images/upload/', views.ajax_image_upload, name='ajax_image_upload'),
]
