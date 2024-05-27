from django.urls import path, register_converter

from apis.pi.accounts import views
from apps.common import converters

register_converter(converters.B64Converter, "b64")

urlpatterns = [
    path("signup/check-user", views.CheckUserAPIView.as_view(), name="check_user"),
    path(
        "signup/send-token",
        views.SendSignupTokenAPIView.as_view(),
        name="send_signup_token",
    ),
    path(
        "signup/check-token",
        views.CheckSignupTokenAPIView.as_view(),
        name="check_signup_token",
    ),
    path("signup", views.SignupAPIView.as_view(), name="signup"),
    path("signin", views.SigninAPIView.as_view(), name="signin"),
    path("social-signin", views.SocialSigninAPIView.as_view(), name="social_signin"),
    path("me", views.MeAPIView.as_view(), name="me"),
    path("me/change-avatar", views.ChangeAvatarAPIView.as_view(), name="change_avatar"),
    path("me/refresh-token", views.RefreshTokenAPIView.as_view(), name="refresh_token"),
    path("me/enable-tfa", views.EnableTFAAPIView.as_view(), name="enable_tfa"),
    path("me/disable-tfa", views.DisableTFAAPIView.as_view(), name="disable_tfa"),
    path("me/passwd", views.ChangePasswordAPIView.as_view(), name="change_password"),
    path(
        "me/passwd/send-token",
        views.SendPasswordTokenAPIView.as_view(),
        name="send_password_token",
    ),
    path(
        "me/passwd/check-token",
        views.CheckPasswordTokenAPIView.as_view(),
        name="check_password_token",
    ),
    path(
        "me/passwd/reset", views.ResetPasswordAPIView.as_view(), name="reset_password"
    ),
    path("me/notes", views.NoteAPIView.as_view(), name="note"),
    path(
        "me/notes/<b64:note_id>", views.NoteDetailAPIView.as_view(), name="note_detail"
    ),
    path("comments", views.CommentAPIView.as_view(), name="comment"),
    path(
        "comments/<b64:comment_id>",
        views.CommentDetailAPIView.as_view(),
        name="comment_detail",
    ),
    path("users", views.UserAPIView.as_view(), name="user"),
    path("users/<b64:user_id>", views.UserDetailAPIView.as_view(), name="user_detail"),
]
