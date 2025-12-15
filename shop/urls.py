from django.urls import path, include
from .views import home, product, detail_drone
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', home, name='home'),
    path('product/', product, name='product'),
    path('drone/<int:pk>/', detail_drone, name='detail'),
    path('user/', include('client.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
