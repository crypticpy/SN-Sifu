# dashboard_view.py
import streamlit as st
from app.core.article_processor import ArticleProcessor
from app.utils.visualization import create_bar_chart, create_pie_chart, create_time_series, visualize_embeddings


async def render_dashboard_view(article_processor: ArticleProcessor):
    st.title("Dashboard")

    await display_statistics(article_processor)
    await display_embeddings_visualization(article_processor)


async def display_statistics(article_processor: ArticleProcessor):
    stats = await article_processor.get_item_statistics()

    st.subheader("Overall Statistics")
    col1, col2 = st.columns(2)
    col1.metric("Total KB Articles", stats['total_kb_articles'])
    col2.metric("Total Tickets", stats['total_tickets'])

    st.subheader("KB Article Categories")
    fig_categories = create_bar_chart(stats['kb_article_categories'], "KB Article Categories")
    st.plotly_chart(fig_categories)

    st.subheader("Ticket Quality Distribution")
    fig_quality = create_pie_chart(stats['ticket_quality_distribution'], "Ticket Quality Distribution")
    st.plotly_chart(fig_quality)

    st.subheader("User Proficiency Distribution")
    fig_proficiency = create_pie_chart(stats['user_proficiency_distribution'], "User Proficiency Distribution")
    st.plotly_chart(fig_proficiency)

    st.subheader("Daily Ticket Count (Last 30 Days)")
    daily_counts = await article_processor.get_daily_ticket_counts(30)
    dates = list(daily_counts.keys())
    counts = list(daily_counts.values())
    fig_time_series = create_time_series(dates, counts, "Daily Ticket Count")
    st.plotly_chart(fig_time_series)


async def display_embeddings_visualization(article_processor: ArticleProcessor):
    st.subheader("Embedding Visualization")
    item_type = st.radio("Select item type", ["KB Articles", "Tickets"])
    plot_type = st.selectbox("Select plot type", ["2D", "3D", "Heatmap"])

    if st.button("Generate Visualization"):
        with st.spinner("Fetching and processing data..."):
            items = await article_processor.cosmos_manager.get_items_by_type(
                "kb_article" if item_type == "KB Articles" else "ticket"
            )
            embeddings = [item['embedding'] for item in items]
            labels = [item['title'] if item_type == "KB Articles" else item['tracking_index'] for item in items]

            fig = visualize_embeddings(embeddings, labels, plot_type.lower())
            st.plotly_chart(fig)
