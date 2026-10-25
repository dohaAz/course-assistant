"""Student 4: Streamlit UI for the course assistant."""
import streamlit as st
from pipeline import DEFAULT_K, prepare_document, answer_question, llm_settings

st.set_page_config(page_title="UniCourse AI", layout="centered")
llm = llm_settings()

with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Passages to retrieve (top-k)", 1, 8, DEFAULT_K)
    st.caption(f"Model: `{llm['model']}` via {llm['base_url']}")
    st.divider()
    if "chunks" in st.session_state:
        st.caption(f"{st.session_state.doc_name}: {len(st.session_state.chunks)} passages indexed")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []

st.title("UniCourse AI")
st.caption("Ask questions about your university PDF and see cited pages")

uploaded = st.file_uploader("Upload a text-selectable course PDF", type=["pdf"])
if uploaded is not None:
    signature = (uploaded.name, uploaded.size, uploaded.getvalue()[:64])
    if st.session_state.get("file_signature") != signature:
        st.session_state.file_signature = signature
        st.session_state.pop("index", None)
        st.session_state.pop("chunks", None)
        st.session_state.messages = []

if uploaded is not None and st.button("Process PDF", type="primary"):
    try:
        with st.spinner("Extracting text and building FAISS index..."):
            st.session_state.index, st.session_state.chunks = prepare_document(
                uploaded.getvalue(), uploaded.name
            )
        st.session_state.doc_name = uploaded.name
        st.success(f"Indexed {len(st.session_state.chunks)} passages from {uploaded.name}")
    except Exception as error:
        st.error(f"Cannot process PDF: {error}")


def show_answer(message: dict):
    st.markdown(message["text"])
    for src in message["sources"]:
        st.caption(f"Source: {src['source']} — p. {src['page']} [{src['chunk_id']}]")
    if not message["sources"]:
        st.info("No verifiable source IDs were returned; check this answer manually.")
    if message["passages"]:
        with st.expander(f"Retrieved passages ({len(message['passages'])})"):
            for p in message["passages"]:
                st.markdown(f"**[{p['chunk_id']}]** p. {p['page']} · score {p['score']:.2f}")
                st.caption(p["text"])


for message in st.session_state.get("messages", []):
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["text"])
        else:
            show_answer(message)

ready = "index" in st.session_state
question = st.chat_input("Ask something about the uploaded lecture..." if ready
                         else "Upload and process a PDF first", disabled=not ready)
if question:
    st.session_state.setdefault("messages", []).append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Retrieving sources and generating answer..."):
                result = answer_question(question, st.session_state.index, st.session_state.chunks,
                                         k=top_k)
            message = {"role": "assistant", "text": result["answer"], "sources": result["sources"],
                       "passages": result["passages"]}
            show_answer(message)
            st.session_state.messages.append(message)
        except Exception as error:
            hint = " Is the LLM server (Ollama) running?" if "connect" in str(error).lower() else ""
            st.error(f"Generation failed: {error}.{hint}")
