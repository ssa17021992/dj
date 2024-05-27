from graphene import ObjectType, Schema

from apis.gql.accounts.mutations import Mutation as AccountsMutation
from apis.gql.accounts.queries import Query as AccountsQuery
from apis.gql.common.mutations import Mutation as CommonMutation
from apis.gql.common.queries import Query as CommonQuery

__all__ = ("schema",)


class Mutation(AccountsMutation, CommonMutation, ObjectType):
    """Mutation type"""

    pass


class Query(AccountsQuery, CommonQuery, ObjectType):
    """Query type"""

    pass


schema = Schema(query=Query, mutation=Mutation)
