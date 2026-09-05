from services.shared.src.modules.configs.project import ProjectConfig

def test_project_config_values():
    assert isinstance(ProjectConfig.project_name, str)
