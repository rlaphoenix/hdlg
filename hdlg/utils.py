import re


CAMEL_TO_SNAKE_1 = re.compile(r"(.)([A-Z][a-z]+)")
CAMEL_TO_SNAKE_2 = re.compile(r"([a-z0-9])([A-Z])")


def camel_to_snake(name: str) -> str:
    """
    Convert CamelCase to snake_case supporting a wide variety of scenarios.

    Examples:
        >>> camel_to_snake("CamelCaseName")
        camel_case_name
        >>> camel_to_snake("camel2_camel2_case")
        camel2_camel2_case
        >>> camel_to_snake("getHTTPResponseCode")
        get_http_response_code
        >>> camel_to_snake("HTTPResponseCodeXYZ")
        http_response_code_xyz
    """
    name = CAMEL_TO_SNAKE_1.sub("\1_\2", name)
    name = CAMEL_TO_SNAKE_2.sub("\1_\2", name)
    return name.lower()
