import graphene
from django.core.cache import cache
from django.utils import timezone

from apis.gql.common import types
from apis.gql.common.enums import FruitType
from apps.common.utils import unique_id
from apps.gql.fields import CursorConnectionField


class FruitQuery:
    """Fruit query type"""

    fruits = CursorConnectionField(
        types.FruitConnection,
        search=graphene.String(required=False),
        description="Fruits.",
    )
    fruit = graphene.Node.Field(types.Fruit, description="Fruit.")

    @classmethod
    def resolve_fruits(cls, root, info, search=None, **kwargs):
        fruits = cache.get("fruits")
        if not fruits:
            fruits = [
                {
                    "id": unique_id(11),
                    "name": f"Orange {x}",
                    "type": FruitType.CITRUS.value,
                    "created": timezone.now(),
                }
                for x in range(1, 1001)
            ]
            cache.set("fruits", fruits, None)
        if search:
            fruits = [fruit for fruit in fruits if fruit["name"].find(search) != -1]
        return fruits


class LocaltimeQuery:
    """Localtime query"""

    localtime = graphene.Field(types.Localtime, description="Localtime.")

    @classmethod
    def resolve_localtime(cls, root, info, **kwargs):
        return {"now": timezone.now()}


class Query(FruitQuery, LocaltimeQuery):
    """Query type"""

    pass
