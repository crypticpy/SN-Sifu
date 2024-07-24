"""
app.py

This is the main Streamlit application for the KB Article and Ticket Processing System.
It provides a user interface for uploading, processing, searching, and visualizing
KB articles and tickets.

Author: Principal Python Engineer
Date: 2024-07-14
"""

import streamlit as st
import asyncio
from app.config import Config
from app.core.article_processor import ArticleProcessor
from app.ui import render_main_view, render_dashboard_view, render_search_view

# Initialize configuration and ArticleProcessor
config = Config.from_env()
article_processor = ArticleProcessor(config)

# Streamlit page configuration
st.set_page_config(page_title="KB Article and Ticket Processor", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Upload and Process", "Dashboard", "Search"])

async def main():
    await article_processor.initialize()

    if page == "Upload and Process":
        await render_main_view(article_processor)
    elif page == "Dashboard":
        await render_dashboard_view(article_processor)
    elif page == "Search":
        await render_search_view(article_processor)

    await article_processor.close()

if __name__ == "__main__":
    asyncio.run(main())