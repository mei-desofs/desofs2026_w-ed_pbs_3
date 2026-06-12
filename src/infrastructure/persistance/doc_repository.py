from sqlalchemy import text
from connection import SessionLocal


class DocumentRepository:

    # ================= CREATE =================
    def create(self, id, workspace_id, title, markdown_content, file_path, created_by):

        db = SessionLocal()
        try:
            db.execute(text("""
                INSERT INTO documents (
                    id,
                    workspace_id,
                    title,
                    markdown_content,
                    file_path,
                    created_by
                )
                VALUES (
                    :id,
                    :workspace_id,
                    :title,
                    :markdown_content,
                    :file_path,
                    :created_by
                )
            """), {
                "id": id,
                "workspace_id": workspace_id,
                "title": title,
                "markdown_content": markdown_content,
                "file_path": file_path,
                "created_by": created_by
            })

            db.commit()

        finally:
            db.close()

    # ================= LIST BY WORKSPACE =================
    def get_by_workspace(self, workspace_id, user_id):

        db = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT id, title, created_at
                FROM documents
                WHERE workspace_id = :workspace_id
                  AND created_by = :user_id
                ORDER BY created_at DESC
            """), {
                "workspace_id": workspace_id,
                "user_id": user_id
            })

            rows = result.fetchall()

            return [
                {
                    "id": r[0],
                    "title": r[1],
                    "created_at": r[2].isoformat() if r[2] else None
                }
                for r in rows
            ]

        finally:
            db.close()

    # ================= GET SINGLE DOC =================
    def get_by_id(self, doc_id, user_id):

        db = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT id, workspace_id, title, markdown_content, file_path, created_at
                FROM documents
                WHERE id = :id
                  AND created_by = :user_id
            """), {
                "id": doc_id,
                "user_id": user_id
            })

            row = result.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "workspace_id": row[1],
                "title": row[2],
                "markdown_content": row[3],
                "file_path": row[4],
                "created_at": row[5].isoformat() if row[5] else None
            }

        finally:
            db.close()

    # ================= DELETE =================
    def delete(self, doc_id, user_id):

        db = SessionLocal()
        try:
            result = db.execute(text("""
                DELETE FROM documents
                WHERE id = :id
                  AND created_by = :user_id
            """), {
                "id": doc_id,
                "user_id": user_id
            })

            db.commit()

            return result.rowcount > 0

        finally:
            db.close()