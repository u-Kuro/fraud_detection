from services.shared.src.modules.logging.logging import logger

def test_logger_is_not_none():
    assert logger is not None

def test_logger_has_info_method():
    assert callable(logger.info)

def test_logger_has_debug_method():
    assert callable(logger.debug)

def test_logger_has_warning_method():
    assert callable(logger.warning)

def test_logger_has_error_method():
    assert callable(logger.error)

def test_logger_has_exception_method():
    assert callable(logger.exception)
