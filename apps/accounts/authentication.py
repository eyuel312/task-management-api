from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token


class StrictTokenAuthentication(TokenAuthentication):
    """
    Custom token authentication that strictly validates tokens.
    Rejects invalid tokens and ensures token exists in database.
    Handles both 'Token <token>' and just '<token>' formats for Swagger compatibility.
    """
    
    def authenticate(self, request):
        """
        Override to ensure strict token validation.
        Returns None if no token is provided, allowing other auth methods.
        Raises AuthenticationFailed if token is invalid.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        # If no Authorization header, return None to allow other auth methods
        if not auth_header:
            return None
        
        # Handle both 'Token <token>' and just '<token>' formats
        token_key = None
        if auth_header.startswith('Token '):
            # Standard format: Token <token>
            try:
                token_key = auth_header.split('Token ')[1].strip()
            except IndexError:
                return None
        elif auth_header.startswith('Bearer '):
            # Bearer format (sometimes used by Swagger)
            try:
                token_key = auth_header.split('Bearer ')[1].strip()
            except IndexError:
                return None
        else:
            # Try as raw token (Swagger might send just the token)
            # But first try parent class method which expects 'Token <token>' format
            result = super().authenticate(request)
            if result:
                return result
            # If parent didn't work, try raw token
            token_key = auth_header.strip()
        
        if not token_key:
            return None
        
        # Validate token exists and is valid
        try:
            token = Token.objects.select_related('user').get(key=token_key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')
        
        # Check if user is active
        if not token.user.is_active:
            raise AuthenticationFailed('User account is disabled.')
        
        return (token.user, token)


