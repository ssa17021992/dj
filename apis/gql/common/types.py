import graphene
from django.core.cache import cache

from apis.gql.common.enums import FruitType
from apps.gql.connections import Connection
from apps.gql.fields import DateTimeTZ


class Fruit(graphene.ObjectType, interfaces=(graphene.Node,)):
    """Fruit type"""

    name = graphene.String(required=True)
    type = graphene.NonNull(FruitType)
    created = DateTimeTZ(required=True)

    @classmethod
    def get_node(cls, info, id):
        for fruit in cache.get("fruits", []):
            if fruit["id"] == id:
                return fruit


class FruitConnection(Connection):
    """Fruit connection"""

    class Meta:
        node = Fruit


class Localtime(graphene.ObjectType):
    """Localtime type"""

    now = DateTimeTZ(required=True)
