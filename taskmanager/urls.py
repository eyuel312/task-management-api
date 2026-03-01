from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.core.views import APIRootView  # Import the root view

schema_view = get_schema_view(
    openapi.Info(
        title="Task Management API",
        default_version='v1',
        description="""
        API for managing tasks and projects.
        
        ## Authentication
        To authenticate, click the "Authorize" button and enter your token in the format:
        ```
        Token <your_token>
        ```
        
        Example: `Token abc123def456ghi789`
        
        After logging in via `/api/auth/login/`, copy the token from the response and use it in the Authorization field.
        """,
        contact=openapi.Contact(email="your-email@example.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],  # Disable authentication for schema view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', APIRootView.as_view(), name='api-root'),  # Root endpoint
    path('api/auth/', include('apps.accounts.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/projects/', include('apps.projects.urls')),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)