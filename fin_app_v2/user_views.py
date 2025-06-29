# user_views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .user_serializers import (
    UserListSerializer, UserDetailSerializer,
    UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer
)


class IsSuperUser(IsAuthenticated):
    """Custom permission to only allow superusers"""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_superuser


# ============ AUTHENTICATION VIEWS ============

class CustomAuthToken(ObtainAuthToken):
    """Get authentication token for superusers only"""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if not user.is_superuser:
            return Response({'error': 'Only superusers can access this API'}, status=status.HTTP_403_FORBIDDEN)

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'is_superuser': user.is_superuser
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login with session authentication"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if user and user.is_superuser:
        login(request, user)
        return Response({
            'message': 'Login successful',
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'is_superuser': user.is_superuser
        })

    return Response({'error': 'Invalid credentials or not superuser'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_view(request):
    """Logout user"""
    logout(request)
    return Response({'message': 'Logout successful'})


@api_view(['GET'])
def check_auth(request):
    """Check authentication status"""
    if request.user.is_authenticated and request.user.is_superuser:
        return Response({
            'authenticated': True,
            'user_id': request.user.pk,
            'username': request.user.username,
            'email': request.user.email,
            'is_superuser': request.user.is_superuser
        })
    return Response({'authenticated': False}, status=status.HTTP_401_UNAUTHORIZED)


# ============ USER MANAGEMENT VIEWS ============

class UserListCreateAPIView(generics.ListCreateAPIView):
    """List all users or create new user"""
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [IsSuperUser]

    def get_serializer_class(self):
        return UserCreateSerializer if self.request.method == 'POST' else UserListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        is_staff = self.request.query_params.get('is_staff')
        if is_staff is not None:
            queryset = queryset.filter(is_staff=is_staff.lower() == 'true')

        return queryset


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete user"""
    queryset = User.objects.all()
    permission_classes = [IsSuperUser]

    def get_serializer_class(self):
        return UserUpdateSerializer if self.request.method in ['PUT', 'PATCH'] else UserDetailSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response({'error': 'Cannot delete your own account'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([IsSuperUser])
def change_user_password(request, pk):
    """Change user password"""
    user = get_object_or_404(User, pk=pk)
    serializer = PasswordChangeSerializer(data=request.data)

    if serializer.is_valid():
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully'})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsSuperUser])
def toggle_user_active(request, pk):
    """Toggle user active status"""
    user = get_object_or_404(User, pk=pk)

    if user == request.user:
        return Response({'error': 'Cannot deactivate your own account'}, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = not user.is_active
    user.save()

    return Response({
        'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
        'is_active': user.is_active
    })


@api_view(['GET'])
@permission_classes([IsSuperUser])
def user_stats(request):
    """Get user statistics"""
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    superusers = User.objects.filter(is_superuser=True).count()

    return Response({
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': total_users - active_users,
        'staff_users': staff_users,
        'superusers': superusers,
        'regular_users': total_users - staff_users
    })


@api_view(['POST'])
@permission_classes([IsSuperUser])
def bulk_user_action(request):
    """Bulk actions on users"""
    user_ids = request.data.get('user_ids', [])
    action = request.data.get('action')

    if not user_ids or not action:
        return Response({'error': 'user_ids and action required'}, status=status.HTTP_400_BAD_REQUEST)

    if request.user.id in user_ids:
        return Response({'error': 'Cannot perform bulk actions on yourself'}, status=status.HTTP_400_BAD_REQUEST)

    users = User.objects.filter(id__in=user_ids)

    if action == 'activate':
        users.update(is_active=True)
        message = f'{users.count()} users activated'
    elif action == 'deactivate':
        users.update(is_active=False)
        message = f'{users.count()} users deactivated'
    elif action == 'delete':
        count = users.count()
        users.delete()
        message = f'{count} users deleted'
    else:
        return Response({'error': 'Invalid action. Use: activate, deactivate, or delete'},
                        status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': message})