import logging, os, sys

class ProxyLogger:
    def __getattr__(self, name: str):
        frame = sys._getframe(1)
        module_spec = frame.f_globals.get("__spec__")
        module_name = getattr(module_spec, "name", None)
        if module_name is None:
            module_name = frame.f_globals.get("__name__") or os.path.splitext(
                os.path.basename(frame.f_code.co_filename)
            )[0]
        return getattr(logging.getLogger(module_name), name)