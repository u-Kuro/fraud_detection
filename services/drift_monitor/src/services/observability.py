from services.drift_monitor.src.modules.environment import environment
from services.shared.observability import Observability

observability: Observability = Observability(environment)