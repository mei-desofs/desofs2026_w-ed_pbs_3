import re


class InvalidWorkspaceNameError(Exception):
    pass


WORKSPACE_NAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]{1,50}$")


def validate_workspace_name(name: str) -> str:
    if not name:
        raise InvalidWorkspaceNameError("Workspace name is required")

    name = name.strip()

    if not WORKSPACE_NAME_REGEX.fullmatch(name):
        raise InvalidWorkspaceNameError(
            "Invalid workspace name. Only letters, numbers, '_' and '-' allowed (max 50 chars)."
        )

    return name