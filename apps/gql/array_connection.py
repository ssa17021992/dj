from graphql_relay import Connection, Edge, PageInfo
from graphql_relay.utils.base64 import base64, unbase64


def get_connection(objects, cursor_field, connection_type, edge_type, page_info_type):
    edges = [
        edge_type(node=obj, cursor=get_cursor(obj, cursor_field)) for obj in objects
    ]
    if edges:
        start_cursor, end_cursor = edges[0].cursor, edges[-1].cursor
    else:
        start_cursor, end_cursor = None, None
    return connection_type(
        edges=edges,
        pageInfo=page_info_type(
            startCursor=start_cursor,
            endCursor=end_cursor,
            hasPreviousPage=True,
            hasNextPage=True,
        ),
    )


def connection_from_queryset(
    queryset,
    limit,
    args,
    cursor_field,
    connection_type=Connection,
    edge_type=Edge,
    page_info_type=PageInfo,
):
    after = cursor_decode(args.get("after"))
    before = cursor_decode(args.get("before"))
    queryset = queryset.order_by(cursor_field)
    asc = True

    if cursor_field.startswith("-"):
        cursor_field = cursor_field[1:]
        asc = False

    if after:
        lookup = "gt" if asc else "lt"
        queryset = queryset.filter(**{f"{cursor_field}__{lookup}": after})
        before = None
    elif before:
        lookup = "lt" if asc else "gt"
        queryset = queryset.filter(**{f"{cursor_field}__{lookup}": before})

    if before or (args.get("last") and not after and not before):
        objects = reversed(queryset.reverse()[:limit])
    else:
        objects = queryset[:limit]

    return get_connection(
        objects, cursor_field, connection_type, edge_type, page_info_type
    )


def connection_from_objects(
    objects,
    limit,
    args,
    cursor_field,
    connection_type=Connection,
    edge_type=Edge,
    page_info_type=PageInfo,
):
    after = cursor_decode(args.get("after"))
    before = cursor_decode(args.get("before"))

    if cursor_field.startswith("-"):
        cursor_field = cursor_field[1:]
        objects = objects[::-1]

    if after:
        index = object_index(objects, cursor_field, after)
        if index is not None:
            objects = objects[index + 1 :]
        before = None
    elif before:
        index = object_index(objects, cursor_field, before)
        if index is not None:
            objects = objects[:index]

    if before or (args.get("last") and not after and not before):
        objects = objects[-limit:]
    else:
        objects = objects[:limit]

    return get_connection(
        objects, cursor_field, connection_type, edge_type, page_info_type
    )


def get_cursor(obj, field):
    if isinstance(obj, dict):
        value = obj.get(field)
    else:
        value = getattr(obj, field, None)
    return cursor_encode(str(value))


def cursor_encode(value):
    if not isinstance(value, str):
        return None
    return base64(value)


def cursor_decode(value):
    if not isinstance(value, str):
        return None
    return unbase64(value)


def object_index(objects, field, value):
    for index, obj in enumerate(objects):
        if isinstance(obj, dict) and obj.get(field) == value:
            return index
        if getattr(obj, field, None) == value:
            return index
