from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path

from apis.ws.accounts.urls import urlpatterns as accounts_urlpatterns
from apis.ws.common.consumers import NotFoundConsumer
from apis.ws.common.urls import urlpatterns as common_urlpatterns


async def asgi_application(scope, receive, send):
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"text/html; charset=utf-8")],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": b"",
        }
    )


apps_urlrouter = URLRouter(
    [
        path("accounts/", URLRouter(accounts_urlpatterns)),
        path("common/", URLRouter(common_urlpatterns)),
    ]
)

ws_urlrouter = URLRouter(
    [
        path("v1/", apps_urlrouter, name="v1"),
        path("v2/", apps_urlrouter, name="v2"),
    ]
)

application = ProtocolTypeRouter(
    {
        "http": asgi_application,
        "websocket": URLRouter(
            [
                path("ws/", ws_urlrouter, name="ws"),
                re_path(r"^", NotFoundConsumer.as_asgi(), name="not_found"),
            ]
        ),
    }
)
