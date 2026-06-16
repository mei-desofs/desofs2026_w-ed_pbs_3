import re

class InvalidWorkspaceNameError(Exception):
    pass


WORKSPACE_NAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]{1,32}$")


def validate_workspace_name(name: str) -> str:
    if not name:
        raise InvalidWorkspaceNameError("Workspace name is required")

    name = name.strip()

    if not WORKSPACE_NAME_REGEX.fullmatch(name):
        raise InvalidWorkspaceNameError(
            "Invalid name: max 32 chars, only letters, numbers, '_' and '-' allowed."
        )

    return name

def sanitize_filename(filename):
    if filename is None:
        return "document"

    return re.sub(r'[^a-zA-Z0-9._ -]', '_', str(filename))