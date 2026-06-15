from sqlalchemy import text
from connection import SessionLocal

class WorkspaceRepository:

    def create(self, id, name, folder_path, created_by):
        db = SessionLocal()
        try:
            db.execute(text("""
                INSERT INTO workspaces (id, name, folder_path, created_by)
                VALUES (:id, :name, :folder_path, :created_by)
            """), {
                "id": id,
                "name": name,
                "folder_path": folder_path,
                "created_by": created_by
            })

            db.commit()
            return id
        finally:
            db.close()

    def get_by_user(self, user_id):
        db = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT
                    w.id,
                    w.name,
                    w.created_at,
                    wm.role
                FROM workspaces w
                JOIN workspace_members wm
                    ON w.id = wm.workspace_id
                WHERE wm.user_id = :user_id
            """), {
                "user_id": user_id
            })

            rows = result.fetchall()

            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "created_at": r[2].isoformat() if r[2] else None,
                    "role": r[3]
                }
                for r in rows
            ]

        finally:
            db.close()


    def count_by_user(self, user_id):
        db = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT COUNT(*) as total
                FROM workspaces
                WHERE created_by = :user_id
            """), {"user_id": user_id})

            return result.fetchone()[0]
        
        finally:
            db.close()

    def delete(self, workspace_id: str) -> bool:
        """
        Remove um workspace da base de dados.

        Arguments:
            workspace_id: Identificador do workspace.

        Returns:
            True se o workspace foi removido, False caso contrário.
        """

        db = SessionLocal()

        try:

            result = db.execute(
                text("""
                    DELETE FROM workspaces
                    WHERE id = :workspace_id
                """),
                {
                    "workspace_id": workspace_id
                }
            )

            db.commit()

            return result.rowcount > 0

        finally:
            db.close()

    def get_by_id(self, workspace_id):

        db = SessionLocal()

        try:

            result = db.execute(text("""
                SELECT
                    id,
                    name,
                    folder_path,
                    created_by,
                    created_at
                FROM workspaces
                WHERE id = :workspace_id
            """), {
                "workspace_id": workspace_id
            })

            row = result.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "name": row[1],
                "folder_path": row[2],
                "created_by": row[3],
                "created_at": row[4]
            }

        finally:
            db.close()