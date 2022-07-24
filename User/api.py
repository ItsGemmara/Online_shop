from re import I
from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import login, logout

from .serializer import *
from .models import CustomUser
from .permissions import AccountIsOwner


class UserViewSet(viewsets.ModelViewSet):
    """
    General ViewSet description
    list: List user
    retrieve: Retrieve user
    update: Update user
    create: Create user
    partial_update: Patch user
    login_user: login user
    unblock_code_generator: unblock code generator
    unblock_account: unblock account
    deactivate_account: deactivate account
    show_pk: show pk for user by phone_number
    """
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer

    def get_permissions(self):
        if self.action == 'update' or self.action == 'partial_update':
            permission_classes = [permissions.IsAuthenticated(), AccountIsOwner()]
            return permission_classes
        return [permissions.AllowAny(), ]

    def get_serializer_class(self):
        if self.action == 'create':
            return SignUpSerializer
        if self.action == 'login':
            return LoginSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UpdateUserSerializer
        return LoginSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    @action(methods=["post"], detail=False)
    def login(self, request):
        serializer = LoginSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)        
        user = serializer.validated_data["user"]
        if user:
            login(self.request, user)
        return Response('done' ,status=200)
    
    @action(methods=["post"], detail=False)
    def logout(self, request):
        logout(request)
        return Response('done' ,status=200)

    




