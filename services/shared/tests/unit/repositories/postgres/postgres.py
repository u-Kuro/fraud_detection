from services.shared.src.repositories.postgres.postgres import sql_session

def test_sql_session_is_sessionmaker():
    from sqlalchemy.orm import sessionmaker
    assert isinstance(sql_session, sessionmaker)

def test_sql_session_module_level_creation(mocker):
    # Verify the module-level sql_session is created without error
    import services.shared.src.repositories.postgres.postgres as module
    assert module.sql_session is not None
