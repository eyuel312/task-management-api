from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from .authentication import StrictTokenAuthentication

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    
    @swagger_auto_schema(
        operation_description="Register a new user account",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'token': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: 'Bad request - Invalid data'
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = (AllowAny,)
    
    @swagger_auto_schema(
        operation_description="Login user and get authentication token",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'token': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: 'Invalid credentials'
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [StrictTokenAuthentication]  # Force strict token authentication only
    
    @swagger_auto_schema(
        operation_description="Logout user and invalidate authentication token",
        security=[{'Token': []}],
        responses={
            200: openapi.Response(
                description="Logout successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: 'Unauthorized - Invalid or missing token'
        }
    )
    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'})

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [StrictTokenAuthentication]  # Force strict token authentication only
    
    @swagger_auto_schema(
        operation_description="Get current authenticated user profile",
        security=[{'Token': []}],
        responses={
            200: UserSerializer,
            401: 'Unauthorized - Invalid or missing token'
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        # Ensure we're using the token-authenticated user, not session user
        if hasattr(self.request, 'auth') and self.request.auth:
            # Token authentication was used
            return self.request.user
        # Fallback to request.user (shouldn't happen with TokenAuthentication only)
        return self.request.user