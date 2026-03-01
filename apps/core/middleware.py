from django.utils.deprecation import MiddlewareMixin


class CsrfExemptApiMiddleware(MiddlewareMixin):
    """
    Middleware to exempt API endpoints and Swagger/ReDoc from CSRF protection.
    API endpoints use token authentication, so CSRF is not needed.
    """
    
    def process_request(self, request):
        # Exempt all API endpoints and Swagger/ReDoc from CSRF
        if (request.path.startswith('/api/') or 
            request.path.startswith('/swagger/') or 
            request.path.startswith('/redoc/')):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None

