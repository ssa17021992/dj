from django.conf import settings
from django.urls import include, path
from django.views.generic import TemplateView

apps_urlpatterns = [
    path(
        "accounts/",
        include(("apis.pi.accounts.urls", "accounts"), namespace="accounts"),
    ),
    path("common/", include(("apis.pi.common.urls", "common"), namespace="common")),
]

if settings.DRF_SWAGGER:
    apps_urlpatterns.append(
        path(
            "docs",
            TemplateView.as_view(
                template_name="swagger.html",
                extra_context={"schema": "openapi/pi.yaml"},
            ),
            name="docs",
        )
    )

urlpatterns = [
    path("v1/", include((apps_urlpatterns, "v1"), namespace="v1")),
    path("v2/", include((apps_urlpatterns, "v2"), namespace="v2")),
]
