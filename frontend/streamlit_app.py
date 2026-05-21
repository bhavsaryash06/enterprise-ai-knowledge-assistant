import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="Enterprise AI Knowledge Assistant",
    page_icon="🤖",
    layout="wide",
)


st.title("Enterprise AI Knowledge Assistant")
st.caption(
    "RAG assistant with Qdrant retrieval, query rewriting, reranking, citations, "
    "evidence checking, LangGraph workflow, and document ingestion."
)


def safe_api_call(method: str, endpoint: str, **kwargs):
    url = f"{API_BASE_URL}{endpoint}"

    if method == "GET":
        response = requests.get(url, timeout=120, **kwargs)
    elif method == "POST":
        response = requests.post(url, timeout=120, **kwargs)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    response.raise_for_status()
    return response.json()


def get_documents() -> list[dict]:
    return safe_api_call("GET", "/documents/")


def upload_document(
    uploaded_file,
    document_name: str,
    department: str | None,
    document_type: str | None,
    version: str | None,
) -> dict:
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }

    data = {
        "document_name": document_name,
        "department": department or "",
        "document_type": document_type or "",
        "version": version or "",
    }

    return safe_api_call(
        "POST",
        "/documents/upload",
        files=files,
        data=data,
    )


def process_document(document_id: str) -> dict:
    return safe_api_call("POST", f"/documents/{document_id}/process")


def chunk_document(document_id: str) -> dict:
    return safe_api_call("POST", f"/documents/{document_id}/chunk")


def index_document(document_id: str) -> dict:
    return safe_api_call("POST", f"/documents/{document_id}/index")


def ask_assistant(payload: dict, api_mode: str) -> dict:
    endpoint = "/ask/graph" if api_mode == "LangGraph Workflow" else "/ask/"
    return safe_api_call("POST", endpoint, json=payload)


ask_tab, document_tab = st.tabs(["Ask Assistant", "Document Management"])


with ask_tab:
    with st.sidebar:
        st.header("Ask Settings")

        api_mode = st.selectbox(
            "API Mode",
            options=["LangGraph Workflow", "Standard RAG Pipeline"],
        )

        top_k = st.slider(
            "Number of chunks to use",
            min_value=1,
            max_value=10,
            value=5,
        )

        use_query_rewrite = st.checkbox(
            "Use query rewriting",
            value=True,
        )

        use_reranking = st.checkbox(
            "Use reranking",
            value=True,
        )

        department = st.selectbox(
            "Department filter",
            options=[
                "None",
                "Finance",
                "Human Resources",
                "Information Technology",
                "Operations",
                "Compliance",
            ],
        )

        document_type = st.selectbox(
            "Document type filter",
            options=["Policy", "None"],
        )

    question = st.text_area(
        "Ask a company policy question",
        placeholder="Example: Can I get reimbursed for a home office monitor?",
        height=100,
    )

    ask_button = st.button("Ask Assistant", type="primary")

    if ask_button:
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            selected_department = None if department == "None" else department
            selected_document_type = None if document_type == "None" else document_type

            payload = {
                "question": question,
                "top_k": top_k,
                "use_query_rewrite": use_query_rewrite,
                "use_reranking": use_reranking,
                "department": selected_department,
                "document_type": selected_document_type,
            }

            with st.spinner("Searching documents and generating answer..."):
                try:
                    result = ask_assistant(payload, api_mode)

                    st.subheader("Answer")
                    st.write(result["answer"])

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Confidence", result.get("confidence", "unknown"))

                    with col2:
                        st.metric(
                            "Escalation Required",
                            str(result.get("escalation_required", False)),
                        )

                    with col3:
                        top_score = result.get("top_score")
                        if top_score is not None:
                            st.metric("Top Score", round(top_score, 3))
                        else:
                            st.metric("Top Score", "N/A")

                    st.subheader("Evidence Reason")
                    st.info(result.get("evidence_reason", "No evidence reason returned."))

                    rewritten_query = result.get("rewritten_query")
                    if rewritten_query:
                        st.subheader("Rewritten Query")
                        st.code(rewritten_query)

                    st.subheader("Sources")
                    sources = result.get("sources", [])

                    if not sources:
                        st.warning("No sources returned.")
                    else:
                        for source in sources:
                            with st.expander(
                                f"Source {source.get('source_number')}: "
                                f"{source.get('document_name')}"
                            ):
                                st.write(source.get("source_label"))
                                st.write("Text preview:")
                                st.write(source.get("text_preview"))

                    st.subheader("Retrieved Chunks")
                    retrieved_chunks = result.get("retrieved_chunks", [])

                    if not retrieved_chunks:
                        st.warning("No retrieved chunks returned.")
                    else:
                        for index, chunk in enumerate(retrieved_chunks, start=1):
                            with st.expander(
                                f"Chunk {index}: {chunk.get('document_name')} "
                                f"| Vector Score: {round(chunk.get('score', 0), 3)}"
                            ):
                                st.write("Department:", chunk.get("department"))
                                st.write("Document Type:", chunk.get("document_type"))
                                st.write("Version:", chunk.get("version"))
                                st.write("Chunk ID:", chunk.get("chunk_id"))

                                rerank_score = chunk.get("rerank_score")
                                if rerank_score is not None:
                                    st.write("Rerank Score:", round(rerank_score, 3))

                                st.write("Chunk Text:")
                                st.write(chunk.get("text"))

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Could not connect to FastAPI. Make sure the backend is running "
                        "on http://127.0.0.1:8000."
                    )

                except requests.exceptions.HTTPError as error:
                    st.error(f"API error: {error}")
                    st.write(error.response.text)

                except Exception as error:
                    st.error(f"Unexpected error: {error}")


with document_tab:
    st.header("Document Management")
    st.caption("Upload, process, chunk, and index enterprise documents.")

    st.subheader("Upload Document")

    with st.form("upload_document_form"):
        uploaded_file = st.file_uploader(
            "Choose a .txt or .pdf file",
            type=["txt", "pdf"],
        )

        document_name_input = st.text_input(
            "Document name",
            placeholder="Example: Finance Reimbursement Policy V1",
        )

        department_input = st.selectbox(
            "Department",
            options=[
                "Finance",
                "Human Resources",
                "Information Technology",
                "Operations",
                "Compliance",
                "Other",
            ],
        )

        document_type_input = st.selectbox(
            "Document type",
            options=["Policy", "SOP", "Guide", "Other"],
        )

        version_input = st.text_input(
            "Version",
            value="v1",
        )

        upload_button = st.form_submit_button("Upload Document")

    if upload_button:
        if uploaded_file is None:
            st.warning("Please choose a file to upload.")
        elif not document_name_input.strip():
            st.warning("Please enter a document name.")
        else:
            try:
                upload_result = upload_document(
                    uploaded_file=uploaded_file,
                    document_name=document_name_input,
                    department=department_input,
                    document_type=document_type_input,
                    version=version_input,
                )

                st.success("Document uploaded successfully.")
                st.json(upload_result)

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to FastAPI. Make sure the backend is running."
                )

            except requests.exceptions.HTTPError as error:
                st.error(f"Upload failed: {error}")
                st.write(error.response.text)

            except Exception as error:
                st.error(f"Unexpected error: {error}")

    st.divider()

    st.subheader("Registered Documents")

    refresh_button = st.button("Refresh Documents")

    try:
        documents = get_documents()

        if not documents:
            st.info("No documents found.")
        else:
            st.dataframe(
                documents,
                use_container_width=True,
            )

            document_options = {
                f"{doc.get('document_name')} | {doc.get('document_id')} | {doc.get('status')}": doc
                for doc in documents
            }

            selected_document_label = st.selectbox(
                "Select a document for processing",
                options=list(document_options.keys()),
            )

            selected_document = document_options[selected_document_label]
            selected_document_id = selected_document["document_id"]

            st.write("Selected document ID:")
            st.code(selected_document_id)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Process Text"):
                    with st.spinner("Processing document text..."):
                        result = process_document(selected_document_id)
                        st.success("Document processed.")
                        st.json(result)

            with col2:
                if st.button("Chunk Document"):
                    with st.spinner("Chunking document..."):
                        result = chunk_document(selected_document_id)
                        st.success("Document chunked.")
                        st.json(result)

            with col3:
                if st.button("Index Document"):
                    st.warning(
                        "Indexing creates embeddings and may use OpenAI API credits."
                    )

                    with st.spinner("Indexing document into Qdrant..."):
                        result = index_document(selected_document_id)
                        st.success("Document indexed.")
                        st.json(result)

    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to FastAPI. Make sure the backend is running "
            "on http://127.0.0.1:8000."
        )

    except requests.exceptions.HTTPError as error:
        st.error(f"API error: {error}")
        st.write(error.response.text)

    except Exception as error:
        st.error(f"Unexpected error: {error}")