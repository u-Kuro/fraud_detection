import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine

@pytest.fixture
def mock_dag_sql_session(mocker):
    session_ctx = MagicMock()
    session_ctx.__enter__ = MagicMock(return_value=MagicMock())
    session_ctx.__exit__ = MagicMock(return_value=False)
    mock_session = MagicMock()
    mock_session.begin.return_value = session_ctx
    return mock_session

@pytest.fixture
def mock_airflow_context():
    task_instance = MagicMock()
    task_instance.task_id = "test_task"
    task_instance.dag_id = "test_dag"
    task_instance.run_id = "test_run"
    task_instance.log_url = "http://localhost:8080/log"

    dag_run = MagicMock()
    dag_run.conf = {}

    context = MagicMock()
    context.__getitem__ = MagicMock(
        side_effect=lambda key: {
            "ti": task_instance,
            "dag_run": dag_run,
            "exception": None,
        }[key]
    )
    context.get = MagicMock(
        side_effect=lambda key, default=None: {
            "ti": task_instance,
            "dag_run": dag_run,
            "exception": None,
        }.get(key, default)
    )
    return context

@pytest.fixture
def mock_slack_client(mocker):
    return MagicMock()

@pytest.fixture
def mock_mlflow_client(mocker):
    return MagicMock()

# ---------------------------------------------------------------------------
# Ensure Airflow and its provider modules are importable even when the full
# Airflow stack is not installed in the current environment. We build a
# minimal ModuleType hierarchy so that Python's import machinery treats every
# node as a package (with __path__) and returns MagicMock leaf attributes for
# any name lookup the DAG source files perform at module level.
# ---------------------------------------------------------------------------

def ensure_package_stub(dotted_name: str) -> ModuleType:
    """
    Walk dotted_name left-to-right, ensuring each segment is registered in
    sys.modules as a types.ModuleType with __path__ set (so Python treats it
    as a package).  The final leaf is set to a MagicMock so that attribute
    lookups on it return further MagicMocks automatically.
    """
    parts = dotted_name.split(".")
    for i, _ in enumerate(parts, start=1):
        name = ".".join(parts[:i])
        if name not in sys.modules:
            if i < len(parts):
                # Intermediate node — needs to be a real package stub
                stub = ModuleType(name)
                stub.__path__ = []          # marks it as a package
                stub.__package__ = name
                stub.__spec__ = None
                sys.modules[name] = stub
            else:
                # Leaf — a MagicMock is fine for the actual hook/class lookups
                leaf = MagicMock()
                sys.modules[name] = leaf
                # Also expose it as an attribute on the parent
                if i > 1:
                    parent = sys.modules[".".join(parts[: i - 1])]
                    setattr(parent, parts[i - 1], leaf)
        else:
            existing = sys.modules[name]
            if i > 1 and isinstance(existing, ModuleType):
                parent = sys.modules[".".join(parts[: i - 1])]
                setattr(parent, parts[i - 1], existing)
    return sys.modules[dotted_name]

# All Airflow import paths that DAG source modules reference at the top level
AIRFLOW_STUBS = [
    "airflow.sdk",
    "airflow.sdk.types",
    "airflow.decorators",
    "airflow.models",
    "airflow.models.dag",
    "airflow.operators.python",
    "airflow.providers.postgres.hooks.postgres",
    "airflow.providers.amazon.aws.hooks.s3",
    "airflow.providers.slack.hooks.slack",
    "airflow.providers.cncf.kubernetes.operators.pod",
    "airflow.providers.standard.operators.empty",
    "airflow.providers.http.operators.http",
    "kubernetes",
    "kubernetes.client",
    "kubernetes.client.models",
]

for stub_path in AIRFLOW_STUBS:
    ensure_package_stub(stub_path)

# ---------------------------------------------------------------------------
# Module-level patches — must be started before pytest collects DAG test
# modules, because those test modules import DAG source files that contain
# module-level code which calls Airflow hooks requiring a live Airflow DB.
# Starting patches here (at conftest import time) guarantees they are active
# before any DAG source module is first imported.
# ---------------------------------------------------------------------------

# Use a real SQLite in-memory engine so that SQLAlchemy's sessionmaker
# accepts it without type errors when the DAG Postgres module is imported.
sqlite_engine = create_engine("sqlite:///:memory:")

pg_hook_mock = MagicMock()
pg_hook_mock.return_value.get_sqlalchemy_engine.return_value = sqlite_engine

s3_hook_mock = MagicMock()

slack_hook_mock = MagicMock()
slack_hook_mock.return_value.client = MagicMock()

patchers = [
    patch(
        "airflow.providers.postgres.hooks.postgres.PostgresHook",
        pg_hook_mock,
    ),
    patch(
        "airflow.providers.amazon.aws.hooks.s3.S3Hook",
        s3_hook_mock,
    ),
    patch(
        "airflow.providers.slack.hooks.slack.SlackHook",
        slack_hook_mock,
    ),
]

for patcher in patchers:
    patcher.start()
