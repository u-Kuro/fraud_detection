from services.shared.src.modules.schemas.postgres.projects import Projects

def test_projects_tablename():
    assert Projects.__tablename__ == "projects"

def test_projects_has_id_column():
    assert hasattr(Projects, "id")

def test_projects_has_created_at_column():
    assert hasattr(Projects, "created_at")

def test_projects_has_name_column():
    assert hasattr(Projects, "name")

def test_projects_id_is_uuid_mapped():
    col = Projects.id.property.columns[0]
    assert str(col.type) in ("UUID", "uuid")

def test_projects_name_is_unique():
    col = Projects.name.property.columns[0]
    assert col.unique is True
