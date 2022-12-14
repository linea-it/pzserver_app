from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "display_name")
        # exclude = [
        #     "id",
        #     "password",
        #     "last_login",
        #     "is_superuser",
        #     "email",
        #     "is_staff",
        #     "is_active",
        #     "date_joined",
        #     "groups",
        #     "user_permissions",
        # ]

    def get_display_name(self, obj):
        return obj.profile.display_name
