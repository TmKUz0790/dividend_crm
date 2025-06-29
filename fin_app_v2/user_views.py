# user_views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
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


class UserListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List all users with search and pagination
    POST: Create a new user
    """
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [IsSuperUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        # Filter by status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        is_staff = self.request.query_params.get('is_staff', None)
        if is_staff is not None:
            queryset = queryset.filter(is_staff=is_staff.lower() == 'true')

        return queryset


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve user details
    PUT/PATCH: Update user
    DELETE: Delete user
    """
    queryset = User.objects.all()
    permission_classes = [IsSuperUser]
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserDetailSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        # Prevent deletion of current superuser
        if user == request.user:
            return Response(
                {'error': 'You cannot delete your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([IsSuperUser])
def change_user_password(request, pk):
    """Change password for a specific user"""
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

    # Prevent deactivating current superuser
    if user == request.user:
        return Response(
            {'error': 'You cannot deactivate your own account'},
            status=status.HTTP_400_BAD_REQUEST
        )

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
    """Perform bulk actions on users"""
    user_ids = request.data.get('user_ids', [])
    action = request.data.get('action')

    if not user_ids or not action:
        return Response(
            {'error': 'user_ids and action are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    users = User.objects.filter(id__in=user_ids)

    # Prevent actions on current user
    if request.user.id in user_ids:
        return Response(
            {'error': 'You cannot perform bulk actions on your own account'},
            status=status.HTTP_400_BAD_REQUEST
        )

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
        return Response(
            {'error': 'Invalid action. Use: activate, deactivate, or delete'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({'message': message})