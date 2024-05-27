"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles import views as staticfiles_views
from django.http import HttpResponse
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.views.static import serve as static_serve

admin.site.site_title = _("Django site admin")
admin.site.site_header = _("Django administration")
admin.site.index_title = _("Site administration")
admin.site.site_url = "/admin/"
admin.site.enable_nav_sidebar = False

urlpatterns = []

if settings.USE_ADMIN_SITE:
    urlpatterns.append(path("admin/", admin.site.urls))

if settings.USE_GRAPHQL:
    from django.views.decorators.csrf import csrf_exempt

    from apps.common.decorators import session_user_exempt
    from apps.gql.views import GQLView

    urlpatterns.append(
        path(
            "gql",
            csrf_exempt(
                session_user_exempt(GQLView.as_view(graphiql=settings.GRAPHIQL))
            ),
            name="gql",
        )
    )

if settings.USE_DRF:
    urlpatterns.append(path("pi/", include(("apis.pi.urls", "pi"), namespace="pi")))

if settings.USE_MEDIA:
    urlpatterns.append(
        path(
            "media/<path:path>",
            static_serve,
            {"document_root": settings.MEDIA_ROOT},
            name="media",
        )
    )

if settings.USE_STATIC:
    if settings.DEBUG:
        urlpatterns.append(
            path("static/<path:path>", staticfiles_views.serve, name="static")
        )
    else:
        urlpatterns.append(
            path(
                "static/<path:path>",
                static_serve,
                {"document_root": settings.STATIC_ROOT},
                name="static",
            )
        )

urlpatterns.append(
    path("health-check", lambda request: HttpResponse(b"(^_^)"), name="health_check")
)

urlpatterns.append(path("", lambda request: HttpResponse(), name="root"))
