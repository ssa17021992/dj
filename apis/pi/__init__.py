from rest_framework.exceptions import ErrorDetail
from rest_framework.status import is_client_error
from rest_framework.views import exception_handler as _exception_handler


class ResponseHandler:
    """Response handler"""

    @classmethod
    def parse_error(cls, field, value):
        errors = []

        if isinstance(value, dict):
            for subfield, error in value.items():
                path = f"{field}.{subfield}"
                errors.extend(cls.parse_error(path, error))
        elif isinstance(value, list):
            for index, error in enumerate(value):
                if isinstance(error, ErrorDetail):
                    path = field
                else:
                    path = f"{field}.{index}"
                errors.extend(cls.parse_error(path, error))
        else:
            errors.append(
                {
                    "field": field,
                    "message": str(value),
                }
            )

        return errors

    @classmethod
    def parse_errors(cls, error_dict):
        error_list = []

        for field, value in error_dict.items():
            error_list.extend(cls.parse_error(field, value))
        return {
            "errors": error_list,
        }

    @classmethod
    def process(cls, response):
        status = getattr(response, "status_code", 200)

        if not is_client_error(status):
            return response
        if not hasattr(response.data, "items"):
            return response

        response.data = cls.parse_errors(response.data)
        return response


def exception_handler(exc, context):
    response = _exception_handler(exc, context)
    return ResponseHandler.process(response)
