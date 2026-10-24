"""Student 4: Streamlit UI for the course assistant."""
import streamlit as st
from pipeline import prepare_document, answer_question

st.set_page_config(page_title="UniCourse AI", page_icon="🎓", layout="centered")
st.title("🎓 UniCourse AI")
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
        st.success(f"Indexed {len(st.session_state.chunks)} passages from {uploaded.name}")
    except Exception as error:
        st.error(f"Cannot process PDF: {error}")

for message in st.session_state.get("messages", []):
    with st.chat_message(message["role"]):
        st.markdown(message["text"])
        for src in message.get("sources", []):
            st.caption(f"📄 {src['source']} — p. {src['page']} [{src['chunk_id']}]")

question = st.chat_input("Ask something about the uploaded lecture...")
if question:
    st.session_state.setdefault("messages", []).append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.write(question)
    if "index" not in st.session_state:
        st.warning("Upload and process a PDF first.")
    else:
        with st.chat_message("assistant"):
            try:
                with st.spinner("Retrieving sources and generating answer..."):
                    result = answer_question(question, st.session_state.index, st.session_state.chunks)
                st.write(result["answer"])
                for source in result["sources"]:
                    st.caption(f"📄 {source['source']} — p. {source['page']} [{source['chunk_id']}]")
                if not result["sources"]:
                    st.info("No verifiable source IDs were returned; check this answer manually.")
                st.session_state.messages.append({"role":"assistant", "text":result["answer"], "sources":result["sources"]})
            except Exception as error:
                st.error(f"Generation failed: {error}")
