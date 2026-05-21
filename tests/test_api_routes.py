from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert "message" in data
    assert "docs_url" in data
    assert "graph_ask_url" in data


def test_documents_list_endpoint():
    response = client.get("/documents/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_ask_endpoint_rejects_short_question():
    payload = {
        "question": "Hi",
        "top_k": 5,
        "use_query_rewrite": True,
        "use_reranking": True,
        "department": None,
        "document_type": "Policy",
    }

    response = client.post("/ask/", json=payload)

    assert response.status_code == 422


def test_retrieve_endpoint_rejects_short_question():
    payload = {
        "question": "Hi",
        "top_k": 5,
        "use_query_rewrite": True,
        "use_reranking": True,
        "department": None,
        "document_type": "Policy",
    }

    response = client.post("/ask/retrieve", json=payload)

    assert response.status_code == 422


def test_ask_endpoint_rejects_invalid_top_k():
    payload = {
        "question": "Can I get reimbursed for a monitor?",
        "top_k": 20,
        "use_query_rewrite": True,
        "use_reranking": True,
        "department": None,
        "document_type": "Policy",
    }

    response = client.post("/ask/", json=payload)

    assert response.status_code == 422