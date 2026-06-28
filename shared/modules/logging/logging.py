from logging import Logger
from typing import cast, Any

from shared.modules.logging.proxy_logger import ProxyLogger

logger: Logger = cast(Logger, cast(Any, ProxyLogger()))