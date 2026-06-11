import os

class WorkspaceService:

    BASE_PATH = "/workspaces"

    def create_workspace(self, user_id: str, name: str):

        safe_user = user_id.replace("..", "").replace("/", "")
        safe_name = name.replace("..", "").replace("/", "")

        path = os.path.join(self.BASE_PATH, safe_user, safe_name)

        os.makedirs(path, exist_ok=True)

        return path