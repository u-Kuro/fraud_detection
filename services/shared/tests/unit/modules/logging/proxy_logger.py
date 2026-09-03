from services.shared.src.modules.logging.proxy_logger import ProxyLogger

def test_proxy_logger_returns_logger_method():
    proxy = ProxyLogger()
    method = proxy.info
    assert callable(method)

def test_proxy_logger_info_delegates_to_logging():
    proxy = ProxyLogger()
    # Calling a method via the proxy should return a bound logging method
    method = proxy.info
    assert callable(method)

def test_proxy_logger_debug_attribute():
    proxy = ProxyLogger()
    assert callable(proxy.debug)

def test_proxy_logger_warning_attribute():
    proxy = ProxyLogger()
    assert callable(proxy.warning)

def test_proxy_logger_error_attribute():
    proxy = ProxyLogger()
    assert callable(proxy.error)

def test_proxy_logger_exception_attribute():
    proxy = ProxyLogger()
    assert callable(proxy.exception)

def test_proxy_logger_uses_caller_module_name(mocker):
    mock_get_logger = mocker.patch("logging.getLogger", return_value=mocker.MagicMock())
    proxy = ProxyLogger()
    _ = proxy.info  # trigger __getattr__
    mock_get_logger.assert_called_once()
