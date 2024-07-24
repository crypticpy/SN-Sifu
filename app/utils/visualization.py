"""
visualization.py

This module provides utility functions for creating various visualizations
of KB articles, tickets, and their embeddings. It uses Plotly for interactive
charts and supports integration with Streamlit.

Author: Principal Python Engineer
Date: 2024-07-14
"""

import plotly.graph_objects as go
import plotly.express as px
from sklearn.manifold import TSNE
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def reduce_dimensions(embeddings: List[List[float]], n_components: int = 2) -> np.ndarray:
    """
    Reduce the dimensionality of embeddings using t-SNE.

    Args:
    embeddings: List of embedding vectors
    n_components: Number of dimensions to reduce to (default is 2 for 2D visualization)

    Returns:
    Numpy array of reduced embeddings
    """
    try:
        tsne = TSNE(n_components=n_components, random_state=42)
        return tsne.fit_transform(embeddings)
    except Exception as e:
        logger.error(f"Error in dimension reduction: {str(e)}")
        raise


def create_scatter_plot(reduced_embeddings: np.ndarray, labels: List[str], title: str) -> go.Figure:
    """
    Create a scatter plot of reduced embeddings.

    Args:
    reduced_embeddings: Numpy array of reduced embeddings
    labels: List of labels for each point
    title: Title of the plot

    Returns:
    Plotly Figure object
    """
    df = pd.DataFrame({
        'x': reduced_embeddings[:, 0],
        'y': reduced_embeddings[:, 1],
        'label': labels
    })

    fig = px.scatter(df, x='x', y='y', hover_data=['label'], title=title)
    fig.update_traces(marker=dict(size=10))
    return fig


def create_3d_scatter_plot(reduced_embeddings: np.ndarray, labels: List[str], title: str) -> go.Figure:
    """
    Create a 3D scatter plot of reduced embeddings.

    Args:
    reduced_embeddings: Numpy array of reduced embeddings (should be 3D)
    labels: List of labels for each point
    title: Title of the plot

    Returns:
    Plotly Figure object
    """
    if reduced_embeddings.shape[1] != 3:
        raise ValueError("Embeddings must be 3D for 3D scatter plot")

    df = pd.DataFrame({
        'x': reduced_embeddings[:, 0],
        'y': reduced_embeddings[:, 1],
        'z': reduced_embeddings[:, 2],
        'label': labels
    })

    fig = px.scatter_3d(df, x='x', y='y', z='z', hover_data=['label'], title=title)
    fig.update_traces(marker=dict(size=5))
    return fig


def create_heatmap(similarity_matrix: np.ndarray, labels: List[str], title: str) -> go.Figure:
    """
    Create a heatmap of similarity between embeddings.

    Args:
    similarity_matrix: 2D numpy array of similarities
    labels: List of labels for each row/column
    title: Title of the plot

    Returns:
    Plotly Figure object
    """
    fig = go.Figure(data=go.Heatmap(z=similarity_matrix, x=labels, y=labels))
    fig.update_layout(title=title, xaxis_title="Items", yaxis_title="Items")
    return fig


def visualize_embeddings(embeddings: List[List[float]], labels: List[str], plot_type: str = '2d') -> go.Figure:
    """
    Visualize embeddings based on the specified plot type.

    Args:
    embeddings: List of embedding vectors
    labels: List of labels for each embedding
    plot_type: Type of plot ('2d', '3d', or 'heatmap')

    Returns:
    Plotly Figure object
    """
    try:
        if plot_type == '2d':
            reduced = reduce_dimensions(embeddings, n_components=2)
            return create_scatter_plot(reduced, labels, "2D Visualization of Embeddings")
        elif plot_type == '3d':
            reduced = reduce_dimensions(embeddings, n_components=3)
            return create_3d_scatter_plot(reduced, labels, "3D Visualization of Embeddings")
        elif plot_type == 'heatmap':
            similarity_matrix = np.inner(embeddings, embeddings)
            return create_heatmap(similarity_matrix, labels, "Similarity Heatmap of Embeddings")
        else:
            raise ValueError(f"Unsupported plot type: {plot_type}")
    except Exception as e:
        logger.error(f"Error in visualizing embeddings: {str(e)}")
        raise


def create_bar_chart(data: Dict[str, int], title: str) -> go.Figure:
    """
    Create a bar chart for categorical data.

    Args:
    data: Dictionary of category-count pairs
    title: Title of the chart

    Returns:
    Plotly Figure object
    """
    fig = go.Figure([go.Bar(x=list(data.keys()), y=list(data.values()))])
    fig.update_layout(title=title, xaxis_title="Category", yaxis_title="Count")
    return fig


def create_pie_chart(data: Dict[str, int], title: str) -> go.Figure:
    """
    Create a pie chart for categorical data.

    Args:
    data: Dictionary of category-count pairs
    title: Title of the chart

    Returns:
    Plotly Figure object
    """
    fig = go.Figure(data=[go.Pie(labels=list(data.keys()), values=list(data.values()))])
    fig.update_layout(title=title)
    return fig


def create_time_series(dates: List[str], values: List[float], title: str) -> go.Figure:
    """
    Create a time series line plot.

    Args:
    dates: List of date strings
    values: List of corresponding values
    title: Title of the chart

    Returns:
    Plotly Figure object
    """
    fig = go.Figure([go.Scatter(x=dates, y=values, mode='lines+markers')])
    fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Value")
    return fig


# Example usage
if __name__ == "__main__":
    import streamlit as st

    # Sample data
    sample_embeddings = np.random.rand(100, 1024)
    sample_labels = [f"Item {i}" for i in range(100)]

    st.title("Embedding Visualizations")

    plot_type = st.selectbox("Select plot type", ['2d', '3d', 'heatmap'])
    fig = visualize_embeddings(sample_embeddings, sample_labels, plot_type)
    st.plotly_chart(fig)

    st.title("Categorical Data Visualizations")

    sample_categories = {
        "Technical": 30,
        "Customer Service": 25,
        "Product": 20,
        "Billing": 15,
        "Other": 10
    }

    bar_fig = create_bar_chart(sample_categories, "Article Categories")
    st.plotly_chart(bar_fig)

    pie_fig = create_pie_chart(sample_categories, "Article Category Distribution")
    st.plotly_chart(pie_fig)

    st.title("Time Series Visualization")

    sample_dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D").strftime("%Y-%m-%d").tolist()
    sample_values = np.cumsum(np.random.randn(len(sample_dates))) + 100
    time_series_fig = create_time_series(sample_dates, sample_values, "Daily Ticket Count")
    st.plotly_chart(time_series_fig)
