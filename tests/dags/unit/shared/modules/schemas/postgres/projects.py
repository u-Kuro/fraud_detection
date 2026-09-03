from dags.shared.modules.schemas.postgres.projects import Projects

def test_projects_tablename():
    assert Projects.__tablename__ == "projects"

def test_projects_has_id():
    assert hasattr(Projects, "id")

def test_projects_has_name():
    assert hasattr(Projects, "name")

def test_projects_name_is_unique():
    col = Projects.name.property.columns[0]
    assert col.unique is True
