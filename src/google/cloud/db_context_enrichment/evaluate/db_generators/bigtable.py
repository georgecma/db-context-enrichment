from typing import Any
import yaml
from .base import BaseDBConfigGenerator

class BigtableConfigGenerator(BaseDBConfigGenerator):
    """
    Dedicated generator mapping properties to explicit Bigtable configuration
    topologies. Bypasses the GDA Python SDK to construct the model configuration
    directly, as the SDK may lack native BigtableReference definitions.
    """

    SOURCE_TYPE = "bigtable"
    DIALECT = "bigtable"
    REQUIRED_FIELDS = BaseDBConfigGenerator.REQUIRED_FIELDS | {
        "project",
        "instance",
    }

    def __init__(self, params: dict[str, Any]):
        super().__init__(params)
        self.project = params.get("project")
        self.instance = params.get("instance")

    def generate_db_config(self) -> str:
        db_config = {
            "db_type": "bigtable",
            "dialect": self.DIALECT,
            "database_name": self.instance,
            "database_path": f"projects/{self.project}/instances/{self.instance}",
            "instance_id": self.instance,
            "gcp_project_id": self.project,
            "max_executions_per_minute": 100,
        }
        return yaml.safe_dump(
            db_config, sort_keys=False, default_flow_style=False
        ).strip()

    def build_datasource_reference(self, context_set_id: str):
        raise NotImplementedError(
            "SDK lacks Bigtable support; generate_model_config is overridden to bypass this."
        )

    def generate_model_config(self, context_set_id: str) -> str:
        """
        Overridden to bypass the SDK and construct the GDA context dictionary directly.
        """
        query_context_dict = {
            "datasource_references": {
                "bigtable_reference": {
                    "database_reference": {
                        "project_id": self.project,
                        "instance_id": self.instance,
                    },
                    "agent_context_reference": {
                        "context_set_id": context_set_id
                    }
                }
            }
        }

        model_config = {
            "generator": "query_data_api",
            "project_id": self.project,
            "location": "global",
            "context": query_context_dict,
        }

        return yaml.safe_dump(
            model_config, sort_keys=False, default_flow_style=False
        ).strip()
