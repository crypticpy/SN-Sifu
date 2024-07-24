import streamlit as st
from app.core.article_processor import ArticleProcessor
from app.utils.file_handler import load_and_process_file


async def render_main_view(article_processor: ArticleProcessor):
    st.title("Upload and Process KB Articles or Tickets")

    file_type = st.radio("Select file type:", ('KB Article', 'Ticket'))
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        if st.button("Process File"):
            await process_uploaded_file(uploaded_file, file_type.lower().replace(" ", "_"), article_processor)


async def process_uploaded_file(uploaded_file, file_type, article_processor):
    df, error = load_and_process_file(uploaded_file, file_type)
    if error:
        st.error(error)
        return

    progress_bar = st.progress(0)
    status_text = st.empty()

    processed_items = await article_processor.process_dataframe(df, file_type)

    for i, _ in enumerate(processed_items):
        progress = (i + 1) / len(processed_items)
        progress_bar.progress(progress)
        status_text.text(f"Processing item {i + 1} of {len(processed_items)}")

    status_text.text("Processing complete!")
    st.success(f"Processed {len(processed_items)} items.")