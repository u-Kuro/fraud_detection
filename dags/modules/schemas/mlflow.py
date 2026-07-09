from functools import cached_property

from pydantic import BaseModel, ConfigDict

class ReplaceExpiredChallengerModelConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    expired_registered_model_name: str
    expired_registered_model_version: int
    replacement_registered_model_name: str
    replacement_registered_model_version: int

    @cached_property
    def replacement_registered_model_version_string(self) -> str:
        return str(self.replacement_registered_model_version)

    @classmethod
    def from_context(cls, context: dict) -> "ReplaceExpiredChallengerModelConfigurations":
        return cls(**(context["dag_run"].conf or {}))

class DeleteExpiredRegisteredModelConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    expired_registered_model_name: str
    expired_registered_model_version: int

    @classmethod
    def from_context(cls, context: dict) -> "DeleteExpiredRegisteredModelConfigurations":
        return cls(**(context["dag_run"].conf or {}))

class DeleteExpiredMLflowRunConfigurations(BaseModel):
    model_config = ConfigDict(strict=False)

    expired_run_id: str

    @classmethod
    def from_context(cls, context: dict) -> "DeleteExpiredMLflowRunConfigurations":
        return cls(**(context["dag_run"].conf or {}))