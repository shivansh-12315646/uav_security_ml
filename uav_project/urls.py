from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler403 = 'core.views.errors.handler_403'
handler404 = 'core.views.errors.handler_404'
handler500 = 'core.views.errors.handler_500'

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
