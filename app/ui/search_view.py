import streamlit as st
from app.core.article_processor import ArticleProcessor


async def render_search_view(article_processor: ArticleProcessor):
    st.title("Search KB Articles and Tickets")

    query = st.text_input("Enter your search query")
    item_type = st.radio("Select item type to search:", ('kb_article', 'ticket'))
    top_k = st.slider("Number of results", 1, 20, 5)

    if st.button("Search"):
        await search_items(query, item_type, top_k, article_processor)


async def search_items(query: str, item_type: str, top_k: int, article_processor: ArticleProcessor):
    results = await article_processor.search_similar_items(query, item_type, top_k)
    if results:
        st.subheader("Search Results")
        for item in results:
            st.write(f"ID: {item['id']}")
            st.write(f"Content: {item['content']}")
            st.write(f"Similarity: {item['similarity']:.2f}")
            st.write("---")
    else:
        st.info("No results found.")