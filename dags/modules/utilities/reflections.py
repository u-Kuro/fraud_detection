def get_module_qualified_name(function: callable) -> str:
    return f"{function.__module__}.{function.__qualname__}"