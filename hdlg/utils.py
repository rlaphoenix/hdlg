import re

NEIGHBORING_WHITESPACE = re.compile(r"[\s]{2,}")
CAMEL_TO_SNAKE_1 = re.compile(r"(.)([A-Z][a-z]+)")
CAMEL_TO_SNAKE_2 = re.compile(r"([a-z0-9])([A-Z])")
SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


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


def size_unit(size, base=1000):
    """
    Convert a file size (in bytes) to a Human Readable Prefixed Size Unit.

    Examples:
        >>> size_unit(131)
        131 B
        >>> size_unit(58812)
        58.81 KB
        >>> size_unit(68819826)
        68.81 MB
        >>> size_unit(39756861649)
        39.75 GB
        >>> size_unit(18754875155724)
        18.75 TB
    """
    i = 0
    while size >= base and i < len(SIZE_UNITS) - 1:
        size /= float(base)
        i += 1
    f = ("%.2f" % size).rstrip("0").rstrip(".")
    return "%s %s" % (f, SIZE_UNITS[i])
