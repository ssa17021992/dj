import graphene


class Connection(graphene.relay.Connection):
    """Connection that supports the total count of items in the collection."""

    total_count = graphene.Int(
        required=True, description="The total count of items in the collection."
    )

    class Meta:
        abstract = True

    @classmethod
    def resolve_total_count(cls, root, info, **kwargs):
        if not hasattr(root, "length"):
            return len(root.iterable)
        return root.length
