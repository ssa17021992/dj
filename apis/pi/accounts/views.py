from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from apis.pi import generics, mixins
from apis.pi.accounts import filters, serializers
from apis.pi.accounts.mixins import SigninMixin
from apis.pi.auth import (
    auth_required,
    has_perm,
    passwd_token_required,
    refresh_token_required,
    signup_token_required,
    staff_required,
)
from apis.pi.common.serializers import EmptySerializer
from apis.pi.decorators import pi_lock, pi_throttle
from apps.accounts.models import Note

User = get_user_model()


class EnableTFAAPIView(generics.CustomCreateAPIView):
    """Enable TFA api view"""

    serializer_create_class = serializers.EnableTFASerializer
    serializer_list_class = serializers.ListUserSerializer
    status = status.HTTP_200_OK

    def get_response_data(self, serializer):
        user = serializer.instance
        return {
            "tfa_secret": user.tfa_secret,
            "qr_code": user.totp_qr_code,
            "user": super().get_response_data(serializer),
        }

    @pi_lock(name="EnableTFAAPIView.CREATE")
    @auth_required
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class DisableTFAAPIView(generics.CustomCreateAPIView):
    """Disable TFA api view"""

    serializer_create_class = serializers.DisableTFASerializer
    serializer_list_class = serializers.ListUserSerializer
    status = status.HTTP_200_OK

    def get_response_data(self, serializer):
        user = serializer.instance
        return {
            "tfa_secret": user.tfa_secret,
            "user": super().get_response_data(serializer),
        }

    @pi_lock(name="DisableTFAAPIView.CREATE")
    @auth_required
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class CheckUserAPIView(generics.CustomCreateAPIView):
    """Check user api view"""

    serializer_create_class = serializers.CheckUserSerializer
    exclude_response_data = True
    status = status.HTTP_200_OK


class SendSignupTokenAPIView(generics.CustomCreateAPIView):
    """Send signup token api view"""

    serializer_create_class = serializers.SendSignupTokenSerializer
    exclude_response_data = True
    status = status.HTTP_200_OK


class CheckSignupTokenAPIView(generics.APIView):
    """Check signup token api view"""

    @signup_token_required
    def post(self, *args, **kwargs):
        return Response()


class SignupAPIView(generics.CustomCreateAPIView):
    """Signup api view"""

    serializer_create_class = serializers.SignupSerializer
    exclude_response_data = True

    @pi_lock(name="SignupAPIView.CREATE")
    @signup_token_required
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class SigninAPIView(SigninMixin, generics.CustomCreateAPIView):
    """Signin api view"""

    serializer_create_class = serializers.SigninSerializer
    serializer_list_class = serializers.ListUserSerializer
    status = status.HTTP_200_OK

    @pi_lock(name="SigninAPIView.CREATE")
    @pi_throttle(name="SigninAPIView.CREATE", limit=3, timeout=600)
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class SocialSigninAPIView(SigninMixin, generics.CustomCreateAPIView):
    """Social signin api view"""

    serializer_create_class = serializers.SocialSigninSerializer
    serializer_list_class = serializers.ListUserSerializer
    status = status.HTTP_200_OK

    @pi_lock(name="SocialSigninAPIView.CREATE")
    @pi_throttle(name="SocialSigninAPIView.CREATE", limit=3, timeout=600)
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class RefreshTokenAPIView(mixins.RequestUserMixin, generics.CustomCreateAPIView):
    """Refresh token api view"""

    serializer_create_class = EmptySerializer
    serializer_list_class = serializers.ListUserSerializer
    as_update = True
    status = status.HTTP_200_OK

    def get_response_data(self, serializer):
        user = serializer.instance
        return {
            "token": user.get_token(),
            "user": super().get_response_data(serializer),
        }

    @pi_lock(name="RefreshTokenAPIView.CREATE")
    @refresh_token_required
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class MeAPIView(mixins.RequestUserMixin, generics.RetrieveUpdateAPIView):
    """Me api view"""

    serializer_list_class = serializers.ListUserSerializer
    serializer_update_class = serializers.UpdateUserSerializer

    @auth_required
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @pi_lock(name="MeAPIView.UPDATE")
    @auth_required
    def put(self, *args, **kwargs):
        return super().put(*args, **kwargs)

    @pi_lock(name="MeAPIView.UPDATE")
    @auth_required
    def patch(self, *args, **kwargs):
        return super().patch(*args, **kwargs)


class ChangeAvatarAPIView(mixins.RequestUserMixin, generics.UpdateAPIView):
    """Change avatar api view"""

    parser_classes = (MultiPartParser,)
    serializer_update_class = serializers.ChangeAvatarSerializer

    def get_request_data(self):
        return {"avatar": self.request.FILES.get("avatar")}

    @pi_lock(name="ChangeAvatarAPIView.UPDATE")
    @auth_required
    def put(self, *args, **kwargs):
        return super().put(*args, **kwargs)

    @pi_lock(name="ChangeAvatarAPIView.UPDATE")
    @auth_required
    def patch(self, *args, **kwargs):
        return super().patch(*args, **kwargs)


class ChangePasswordAPIView(mixins.RequestUserMixin, generics.CustomCreateAPIView):
    """Change password api view"""

    serializer_create_class = serializers.ChangePasswordSerializer
    as_update = True
    exclude_response_data = True
    status = status.HTTP_200_OK

    @pi_lock(name="ChangePasswordAPIView.CREATE")
    @auth_required
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class SendPasswordTokenAPIView(generics.CustomCreateAPIView):
    """Send password token api view"""

    serializer_create_class = serializers.SendPasswordTokenSerializer
    exclude_response_data = True
    status = status.HTTP_200_OK


class CheckPasswordTokenAPIView(generics.APIView):
    """Check password token api view"""

    @passwd_token_required
    def post(self, *args, **kwargs):
        return Response()


class ResetPasswordAPIView(mixins.RequestUserMixin, generics.CustomCreateAPIView):
    """Reset password api view"""

    serializer_create_class = serializers.ResetPasswordSerializer
    as_update = True
    exclude_response_data = True
    status = status.HTTP_200_OK

    @passwd_token_required
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class UserAPIView(generics.ListCreateAPIView):
    """User api view"""

    queryset = User.objects.all()
    serializer_create_class = serializers.CreateUserSerializer
    serializer_list_class = serializers.ListUserSerializer
    filterset_class = filters.UserFilter

    @staff_required
    @has_perm("accounts.view_user")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @pi_lock(name="UserAPIView.CREATE")
    @staff_required
    @has_perm("accounts.add_user")
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """User detail api view"""

    queryset = User.objects.all()
    serializer_list_class = serializers.ListUserSerializer
    serializer_update_class = serializers.UpdateUserSerializer
    lookup_url_kwarg = "user_id"

    @staff_required
    @has_perm("accounts.view_user")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @pi_lock(name="UserDetailAPIView.UPDATE")
    @staff_required
    @has_perm("accounts.change_user")
    def put(self, *args, **kwargs):
        return super().put(*args, **kwargs)

    @pi_lock(name="UserDetailAPIView.UPDATE")
    @staff_required
    @has_perm("accounts.change_user")
    def patch(self, *args, **kwargs):
        return super().patch(*args, **kwargs)

    @pi_lock(name="UserDetailAPIView.DELETE")
    @staff_required
    @has_perm("accounts.delete_user")
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)


class NoteAPIView(generics.ListCreateAPIView):
    """Note api view"""

    queryset = Note.objects.all()
    serializer_create_class = serializers.CreateNoteSerializer
    serializer_list_class = serializers.ListNoteSerializer
    filterset_class = filters.NoteFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    @auth_required
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @pi_lock(name="NoteAPIView.CREATE")
    @auth_required
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class NoteDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Note detail api view"""

    queryset = Note.objects.all()
    serializer_list_class = serializers.ListNoteSerializer
    serializer_update_class = serializers.UpdateNoteSerializer
    lookup_url_kwarg = "note_id"

    def get_object(self):
        note = super().get_object()
        if note.user_id != self.request.user.pk:
            raise PermissionDenied({"perm": _("Permission denied.")})
        return note

    @auth_required
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @pi_lock(name="NoteDetailAPIView.UPDATE")
    @auth_required
    def put(self, *args, **kwargs):
        return super().put(*args, **kwargs)

    @pi_lock(name="NoteDetailAPIView.UPDATE")
    @auth_required
    def patch(self, *args, **kwargs):
        return super().patch(*args, **kwargs)

    @pi_lock(name="NoteDetailAPIView.DELETE")
    @auth_required
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)


class CommentAPIView(generics.ListCreateAPIView):
    """Comment api view"""

    queryset = Note.objects.prefetch_related(
        Prefetch(
            "user", queryset=User.objects.only("pk", "email", "first_name", "last_name")
        )
    )
    serializer_create_class = serializers.CreateCommentSerializer
    serializer_list_class = serializers.ListCommentSerializer
    filterset_class = filters.CommentFilter

    @pi_lock(name="CommentAPIView.CREATE")
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Comment detail api view"""

    queryset = Note.objects.prefetch_related(
        Prefetch(
            "user", queryset=User.objects.only("pk", "email", "first_name", "last_name")
        )
    )
    serializer_list_class = serializers.ListCommentSerializer
    serializer_update_class = serializers.UpdateCommentSerializer
    lookup_url_kwarg = "comment_id"

    @transaction.atomic
    def perform_destroy(self, instance):
        instance.delete()
        instance.user.delete()

    @pi_lock(name="CommentDetailAPIView.UPDATE")
    def put(self, *args, **kwargs):
        return super().put(*args, **kwargs)

    @pi_lock(name="CommentDetailAPIView.UPDATE")
    def patch(self, *args, **kwargs):
        return super().patch(*args, **kwargs)

    @pi_lock(name="CommentDetailAPIView.DELETE")
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)
