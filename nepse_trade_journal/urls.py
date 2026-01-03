from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('journal/', include(('journal.urls', 'journal'), namespace='journal')),
    path('portfolio/', include(('portfolio.urls', 'portfolio'), namespace='portfolio')),
    path('learning/', include(('learning.urls', 'learning'), namespace='learning')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
