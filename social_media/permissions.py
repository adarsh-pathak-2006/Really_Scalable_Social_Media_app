from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User=get_user_model()

class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role==User.Moderator

class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role==User.Customer

class IsModeratorAndCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.Moderator, User.Customer]