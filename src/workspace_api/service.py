import os
from src.domain.workspace.workspace_name import validate_workspace_name


class WorkspaceService:

    BASE_PATH = "/workspaces"

    def create_workspace(self, user_id: str, name: str):

        # user_id vem do JWT
        safe_user = str(user_id).strip()

        # validação de domínio
        safe_name = validate_workspace_name(name)

        path = os.path.join(self.BASE_PATH, safe_user, safe_name)

        # proteção extra
        full_path = os.path.abspath(path)
        base_path = os.path.abspath(self.BASE_PATH)

        if not full_path.startswith(base_path):
            raise Exception("Invalid workspace path")

        os.makedirs(full_path, exist_ok=True)

        return full_path