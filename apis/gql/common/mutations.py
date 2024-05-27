import graphene
from django.utils import timezone

from apis.gql.common import inputs, types
from apis.gql.common.decorators import gql_throttle
from apps.common.utils import unique_id
from apps.gql import mutations


class CreateFruit(mutations.Mutation):
    """Create fruit."""

    class Arguments:
        input = inputs.CreateFruitInput(
            required=True, description="Create fruit input."
        )

    class Meta:
        description = "Create fruit."
        field_name = "fruit"
        field_type = types.Fruit

    @classmethod
    def perform_mutation(cls, root, info, input, **kwargs):
        return {
            "id": unique_id(11),
            "created": timezone.now(),
            **input,
        }


class Echo(mutations.Mutation):
    """Echo."""

    class Arguments:
        message = graphene.String(required=True, description="Echo message.")

    class Meta:
        description = "Echo."
        field_name = "message"
        field_type = graphene.String

    @classmethod
    @gql_throttle(name="Echo", limit=10, timeout=60)
    def perform_mutation(cls, root, info, message, **kwargs):
        return message


class FruitMutation:
    """Fruit mutation type"""

    create_fruit = CreateFruit.Field()


class EchoMutation:
    """Echo mutation type"""

    echo = Echo.Field()


class Mutation(FruitMutation, EchoMutation):
    """Mutation type"""

    pass
