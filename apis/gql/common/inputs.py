import graphene

from apis.gql.common.enums import FruitType


class CreateFruitInput(graphene.InputObjectType):
    """Create fruit input."""

    name = graphene.String(required=True)
    type = graphene.NonNull(FruitType)
