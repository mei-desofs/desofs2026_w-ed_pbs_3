import pytest
from unittest.mock import patch, MagicMock


# ================= POST /documents =================

class TestCreateDocument:

    def test_missing_workspace_id_returns_400(self, client, auth_headers):
        resp = client.post("/documents", json={"title": "Teste"}, headers=auth_headers)
        assert resp.status_code == 400
        assert "missing fields" in resp.get_json()["error"]

    def test_missing_title_returns_400(self, client, auth_headers):
        resp = client.post("/documents", json={"workspace_id": "ws-uuid-1"}, headers=auth_headers)
        assert resp.status_code == 400
        assert "missing fields" in resp.get_json()["error"]

    def test_workspace_not_found_returns_404(self, client, auth_headers):
        """Workspace não existe na BD — deve retornar 404."""
        resp = client.post(
            "/documents",
            json={"workspace_id": "ws-inexistente", "title": "Doc"},
            headers=auth_headers
        )
        assert resp.status_code == 404

    def test_workspace_service_failure_returns_500(self, client, auth_headers, seed_workspace):
        """BD ok, mas o serviço workspace falha — deve retornar 500."""
        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("src.API.doc_routes.requests.post", return_value=mock_response):
            resp = client.post(
                "/documents",
                json={"workspace_id": "ws-uuid-1", "title": "Doc", "content": "# Olá"},
                headers=auth_headers
            )
        assert resp.status_code == 500

    def test_success_creates_document(self, client, auth_headers, seed_workspace):
        """Criação bem-sucedida deve retornar id e title e persistir na BD."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("src.API.doc_routes.requests.post", return_value=mock_response):
            resp = client.post(
                "/documents",
                json={"workspace_id": "ws-uuid-1", "title": "Doc Teste", "content": "# Olá"},
                headers=auth_headers
            )

        assert resp.status_code == 200
        body = resp.get_json()
        assert body["title"] == "Doc Teste"
        assert "id" in body

    def test_create_without_jwt_returns_401(self, client):
        resp = client.post("/documents", json={"workspace_id": "ws-uuid-1", "title": "Doc"})
        assert resp.status_code == 401


# ================= GET /documents/<workspace_id> =================

class TestListDocuments:

    def test_returns_list_of_documents(self, client, auth_headers, seed_document):
        resp = client.get("/documents/ws-uuid-1", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert len(body["documents"]) == 1
        assert body["documents"][0]["id"] == "doc-uuid-1"

    def test_returns_empty_list_when_no_documents(self, client, auth_headers, seed_workspace):
        resp = client.get("/documents/ws-uuid-1", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["documents"] == []

    def test_list_without_jwt_returns_401(self, client):
        resp = client.get("/documents/ws-uuid-1")
        assert resp.status_code == 401


# ================= GET /document/<doc_id> =================

class TestGetDocument:

    def test_returns_document_when_found(self, client, auth_headers, seed_document):
        resp = client.get("/document/doc-uuid-1", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["id"] == "doc-uuid-1"
        assert body["title"] == "Doc Teste"

    def test_returns_404_when_not_found(self, client, auth_headers):
        resp = client.get("/document/doc-inexistente", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_without_jwt_returns_401(self, client):
        resp = client.get("/document/doc-uuid-1")
        assert resp.status_code == 401


# ================= PUT /document/<doc_id> =================

class TestUpdateDocument:

    def test_missing_title_returns_400(self, client, auth_headers, seed_document):
        resp = client.put(
            "/document/doc-uuid-1",
            json={"content": "novo conteúdo"},
            headers=auth_headers
        )
        assert resp.status_code == 400

    def test_returns_404_when_document_not_found(self, client, auth_headers):
        resp = client.put(
            "/document/doc-inexistente",
            json={"title": "Novo Título", "content": "novo conteúdo"},
            headers=auth_headers
        )
        assert resp.status_code == 404

    def test_success_updates_document(self, client, auth_headers, seed_document):
        resp = client.put(
            "/document/doc-uuid-1",
            json={"title": "Título Atualizado", "content": "# Novo conteúdo"},
            headers=auth_headers
        )
        assert resp.status_code == 200
        assert "atualizado" in resp.get_json()["message"]

    def test_update_without_jwt_returns_401(self, client):
        resp = client.put("/document/doc-uuid-1", json={"title": "Título"})
        assert resp.status_code == 401


# ================= DELETE /document/<doc_id> =================

class TestDeleteDocument:

    def test_success_deletes_document(self, client, auth_headers, seed_document):
        resp = client.delete("/document/doc-uuid-1", headers=auth_headers)
        assert resp.status_code == 200
        assert "eliminado" in resp.get_json()["message"]

    def test_returns_404_when_not_found(self, client, auth_headers):
        resp = client.delete("/document/doc-inexistente", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_without_jwt_returns_401(self, client):
        resp = client.delete("/document/doc-uuid-1")
        assert resp.status_code == 401