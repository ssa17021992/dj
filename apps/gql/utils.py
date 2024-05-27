from django.core.exceptions import NON_FIELD_ERRORS
from graphene import Node
from graphene.utils.str_converters import to_camel_case, to_snake_case  # noqa
from graphql_relay import from_global_id, to_global_id  # noqa


def node_from_global_id(info, id, only_type=None):
    """Get node from global ID."""
    try:
        node = Node.get_node_from_global_id(info, id, only_type)
    except Exception:
        return None
    return node


def id_from_global_id(id):
    """Get id from global ID."""
    try:
        _, id = from_global_id(id)
    except Exception:
        return None
    return id


def name_from_global_id(id):
    """Get type name from global ID."""
    try:
        name, _ = from_global_id(id)
    except Exception:
        return None
    return name


def validation_error_to_error_list(validation_error):
    """Convert ValidationError to a list of errors."""
    error_list = []
    if hasattr(validation_error, "error_dict"):
        for field, field_errors in validation_error.message_dict.items():
            field = to_camel_case(field) if field != NON_FIELD_ERRORS else None
            error_list.extend(
                [
                    {
                        "field": field,
                        "message": error,
                    }
                    for error in field_errors
                ]
            )
    else:
        error_list.extend(
            [
                {
                    "field": error.code,
                    "message": error.message,
                }
                for error in validation_error.error_list
            ]
        )
    return error_list
