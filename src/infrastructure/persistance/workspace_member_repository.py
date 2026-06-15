from sqlalchemy import text
from connection import SessionLocal


class WorkspaceMemberRepository:

    def add_member(
        self,
        workspace_id: str,
        user_id: str,
        role: str
    ):
        """
        Adiciona um membro a um workspace.

        Arguments:
            workspace_id: ID do workspace.
            user_id: ID do utilizador.
            role: ADMIN, EDITOR ou VIEWER.
        """

        db = SessionLocal()

        try:

            db.execute(text("""
                INSERT INTO workspace_members (
                    workspace_id,
                    user_id,
                    role
                )
                VALUES (
                    :workspace_id,
                    :user_id,
                    :role
                )
            """), {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "role": role
            })

            db.commit()

        finally:
            db.close()

    def get_members(self, workspace_id: str):

        db = SessionLocal()

        try:

            result = db.execute(text("""
                SELECT
                    u.id,
                    u.username,
                    wm.role,
                    wm.joined_at
                FROM workspace_members wm
                JOIN users u
                    ON wm.user_id = u.id
                WHERE wm.workspace_id = :workspace_id
            """), {
                "workspace_id": workspace_id
            })

            rows = result.fetchall()

            return [
                {
                    "id": row[0],
                    "username": row[1],
                    "role": row[2],
                    "joined_at": row[3]
                }
                for row in rows
            ]

        finally:
            db.close()

    def get_role(
        self,
        workspace_id: str,
        user_id: str
    ):

        db = SessionLocal()

        try:

            result = db.execute(text("""
                SELECT role
                FROM workspace_members
                WHERE workspace_id = :workspace_id
                AND user_id = :user_id
            """), {
                "workspace_id": workspace_id,
                "user_id": user_id
            })

            row = result.fetchone()

            if not row:
                return None

            return row[0]

        finally:
            db.close()


    def remove_member(
        self,
        workspace_id: str,
        user_id: str
    ):

        db = SessionLocal()

        try:

            result = db.execute(text("""
                DELETE FROM workspace_members
                WHERE workspace_id = :workspace_id
                AND user_id = :user_id
            """), {
                "workspace_id": workspace_id,
                "user_id": user_id
            })

            db.commit()

            return result.rowcount > 0

        finally:
            db.close()