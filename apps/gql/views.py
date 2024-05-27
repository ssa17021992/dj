import json
from traceback import print_exception

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseNotAllowed
from django.http.response import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from graphene_django.settings import graphene_settings
from graphene_django.views import GraphQLView, HttpError
from graphql import get_introspection_query, parse, validate
from graphql.error import GraphQLError
from graphql.execution import ExecutionResult

from apps.gql.utils import validation_error_to_error_list

capture_exception = lambda *args, **kwargs: None  # noqa

if getattr(settings, "USE_SENTRY", False):
    try:
        from sentry_sdk import capture_exception
    except ImportError:
        pass

graphql_error = (
    GraphQLError,
    HttpError,
    AssertionError,
)
user_settings = graphene_settings.user_settings

MAX_SIZE = user_settings.get("GQL_MAX_SIZE", 2048)
MAX_DEFINITIONS = user_settings.get("GQL_MAX_DEFINITIONS", 10)
MAX_DEPTH = user_settings.get("GQL_MAX_DEPTH", 10)
MAX_FIELDS = user_settings.get("GQL_MAX_FIELDS", 2)
INTROSPECTION = user_settings.get("GQL_INTROSPECTION", True)

cache = {}


def get_fields_names(fields):
    return [field.name.value for field in fields]


def measure_depth(selection_set, depth=1):
    max_depth = depth
    for field in selection_set.selections:
        if not getattr(field, "selection_set", None):
            continue
        new_depth = measure_depth(field.selection_set, depth=depth + 1)
        if new_depth > max_depth:
            max_depth = new_depth
    return max_depth


def measure_alias(selection_set, alias=1):
    max_alias = alias
    fields = get_fields_names(selection_set.selections)

    for field in selection_set.selections:
        if getattr(field, "selection_set", None):
            new_alias = measure_alias(
                field.selection_set, alias=fields.count(field.name.value)
            )
        else:
            new_alias = fields.count(field.name.value)
        if new_alias > max_alias:
            max_alias = new_alias
    return max_alias


def measure_query_fields(definition):
    types = (
        "Query",
        "Mutation",
        "Subscription",
    )
    type_condition = getattr(definition, "type_condition", None)

    if type_condition and type_condition.name.value not in types:
        return 0

    fields = get_fields_names(definition.selection_set.selections)

    if not INTROSPECTION:
        if "__schema" in fields:
            raise GraphQLError("__schema introspection is not allowed.")
        if "__type" in fields:
            raise GraphQLError("__type introspection is not allowed.")
    return len(fields)


def validate_document(document):
    ast = document

    if len(ast.definitions) > MAX_DEFINITIONS:
        raise GraphQLError(
            "Only %d definitions are allowed per query." % MAX_DEFINITIONS
        )

    for definition in ast.definitions:
        if not getattr(definition, "selection_set", None):
            continue

        depth = measure_depth(definition.selection_set)
        if depth > MAX_DEPTH:
            raise GraphQLError("Query depth allowed is %d." % MAX_DEPTH)

        alias = measure_alias(definition.selection_set)
        if alias > 1:
            raise GraphQLError("Only 1 alias is allowed per field.")

        fields = measure_query_fields(definition)
        if fields > MAX_FIELDS:
            raise GraphQLError(
                "Only %d fields are allowed at query level." % MAX_FIELDS
            )
    return document


class GQLView(GraphQLView):
    """GraphQLView with file upload support."""

    graphiql_template = "graphiql.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        try:
            if request.method not in (
                "GET",
                "POST",
            ):
                raise HttpError(
                    HttpResponseNotAllowed(
                        ["GET", "POST"], "Only GET and POST requests are allowed."
                    )
                )
            if self.graphiql and GraphQLView.request_wants_html(request):
                return self.render_graphiql(request)

            data = self.parse_body(request)
            result, status_code = self.get_response(request, data)
            return HttpResponse(
                status=status_code, content=result, content_type="application/json"
            )
        except HttpError as e:
            response = e.response
            response["Content-Type"] = "application/json"
            data = {"errors": self.format_error(e)}
            response.content = self.json_encode(request, data)
            return response

    def get_response(self, request, data):
        query, variables, operation_name = self.get_graphql_params(request, data)
        response = {}
        result = None
        status_code = 200

        if INTROSPECTION and "__schema" in query:
            if "__schema" in cache:
                response["data"] = cache["__schema"]
                result = self.json_encode(request, response)
                return result, status_code
            query = get_introspection_query()

        execution_result = self.execute_graphql_request(
            request, data, query, variables, operation_name
        )
        if not execution_result:
            return result, status_code

        result_errors = execution_result.errors
        if result_errors:
            errors = []
            for error in result_errors:
                errors.extend(self.format_error(error))
            response["errors"] = errors

        result_data = execution_result.data
        if INTROSPECTION and "__schema" in (result_data or {}):
            cache["__schema"] = result_data

        response["data"] = result_data
        result = self.json_encode(request, response)

        return result, status_code

    def execute_graphql_request(self, request, data, query, variables, operation_name):
        if request.method != "POST":
            raise HttpError(
                HttpResponseNotAllowed(["POST"], "Only POST requests are allowed.")
            )
        if not query:
            raise HttpError(HttpResponseBadRequest("Query string is required."))
        query_size = len(query)
        if query_size > MAX_SIZE:
            raise HttpError(
                HttpResponseBadRequest(
                    "Query string size of %d exceeds the limit of %d."
                    % (
                        query_size,
                        MAX_SIZE,
                    )
                )
            )

        try:
            document = parse(query)
        except Exception as e:
            return ExecutionResult(errors=[e])
        try:
            validate_document(document)
        except Exception as e:
            return ExecutionResult(errors=[e])

        validation_errors = validate(self.schema.graphql_schema, document, max_errors=1)
        if validation_errors:
            return ExecutionResult(errors=validation_errors)

        return self.schema.execute(
            source=query,
            root_value=self.get_root_value(request),
            variable_values=variables,
            operation_name=operation_name,
            context_value=self.get_context(request),
        )

    @staticmethod
    def get_graphql_params(request, data):
        content_type = GraphQLView.get_content_type(request)

        if content_type == "multipart/form-data":
            try:
                data = json.loads(data.get("operation"))
                if not isinstance(data, dict):
                    raise ValueError()
            except Exception:
                raise HttpError(HttpResponseBadRequest("Operation is invalid JSON."))

        query = data.get("query")
        variables = data.get("variables")
        operation_name = data.get("operationName")

        if not isinstance(query, str):
            query = ""
        if not isinstance(variables, dict):
            variables = None
        if not isinstance(operation_name, str):
            operation_name = None

        return query, variables, operation_name

    @staticmethod
    def format_error(error):
        while True:
            original_error = getattr(error, "original_error", None)
            if original_error is None:
                break
            error = original_error

        if isinstance(error, ValidationError):
            return validation_error_to_error_list(error)
        if not isinstance(error, graphql_error):
            traceback = getattr(error, "__traceback__", None)
            print_exception(type(error), error, traceback)
            capture_exception(error)

        return [
            {
                "field": None,
                "message": str(error),
            }
        ]
