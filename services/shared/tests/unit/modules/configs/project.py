from services.shared.src.modules.configs.project import ProjectConfig

class TestProjectConfig:
    def test_values(self):
        assert isinstance(ProjectConfig.project_name, str)
