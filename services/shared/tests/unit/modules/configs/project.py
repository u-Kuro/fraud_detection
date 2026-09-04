from services.shared.src.modules.configs.project import ProjectConfig

def test_project_config_project_name_is_string():
    assert isinstance(ProjectConfig.project_name, str)
