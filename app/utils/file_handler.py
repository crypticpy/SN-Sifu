"""
file_handler.py

This module provides utilities for handling file uploads and processing
both KB articles and Ticket Data.

Author: Principal Python Engineer
Date: 2024-07-14
"""

import pandas as pd
import io
from typing import Tuple, Optional, Dict, Any
import logging
from app.config import Config

logger = logging.getLogger(__name__)


def load_and_process_file(file, file_type: str) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Load and process an uploaded file.

    Args:
    file: The uploaded file object
    file_type: Either 'kb_article' or 'ticket'

    Returns:
    Tuple of (DataFrame or None, error message or empty string)
    """
    try:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(file.read()))
        elif file.name.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file.read()))
        else:
            return None, f"Unsupported file type: {file.name}. Please upload .xlsx or .csv files."

        if file_type == 'kb_article':
            return process_kb_article(df)
        elif file_type == 'ticket':
            return process_ticket(df)
        else:
            return None, f"Invalid file type specified: {file_type}"

    except Exception as e:
        logger.error(f"Error processing file {file.name}: {str(e)}")
        return None, f"Error processing file: {str(e)}"


def process_kb_article(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Process and validate KB article data.

    Args:
    df: DataFrame containing KB article data

    Returns:
    Tuple of (Processed DataFrame or None, error message or empty string)
    """
    required_columns = ['KB Article #', 'Version', 'Category', 'Title', 'Introduction', 'Instructions', 'Keywords']

    if not all(col in df.columns for col in required_columns):
        missing_columns = [col for col in required_columns if col not in df.columns]
        return None, f"Missing required columns for KB article: {', '.join(missing_columns)}"

    # Additional processing steps
    df['Updated'] = pd.Timestamp.now().isoformat()
    df['KB Article #'] = df['KB Article #'].astype(str)
    df['Version'] = df['Version'].astype(str)

    # Validate data types
    if not df['KB Article #'].str.match(r'KB\d+').all():
        return None, "Invalid 'KB Article #' format. Should be 'KB' followed by numbers."

    if not df['Version'].str.match(r'\d+\.\d+').all():
        return None, "Invalid 'Version' format. Should be in X.Y format (e.g., 1.0)."

    return df, ""


def process_ticket(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Process and validate Ticket Data.

    Args:
    df: DataFrame containing Ticket Data

    Returns:
    Tuple of (Processed DataFrame or None, error message or empty string)
    """
    required_columns = [
        'tracking_index', 'Description', 'Close Notes', 'summarize_ticket',
        'ticket_quality', 'user_proficiency_level', 'potential_impact',
        'resolution_appropriateness', 'potential_root_cause'
    ]

    if not all(col in df.columns for col in required_columns):
        missing_columns = [col for col in required_columns if col not in df.columns]
        return None, f"Missing required columns for Ticket Data: {', '.join(missing_columns)}"

    # Handle potential missing columns that are not required
    optional_columns = [
        'summarize_ticket_explanation', 'ticket_quality_explanation',
        'user_proficiency_level_explanation', 'potential_impact_explanation',
        'resolution_appropriateness_explanation', 'potential_root_cause_explanation'
    ]

    for col in optional_columns:
        if col not in df.columns:
            df[col] = ''  # Add empty column if missing

    # Additional processing steps
    df['created_at'] = pd.Timestamp.now().isoformat()
    df['tracking_index'] = df['tracking_index'].astype(str)

    # Validate data types and formats
    if not df['tracking_index'].str.match(r'T\d+').all():
        return None, "Invalid 'tracking_index' format. Should be 'T' followed by numbers."

    valid_qualities = ['Poor', 'Fair', 'Good', 'Excellent']
    if not df['ticket_quality'].isin(valid_qualities).all():
        return None, f"Invalid 'ticket_quality'. Should be one of: {', '.join(valid_qualities)}"

    valid_proficiencies = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    if not df['user_proficiency_level'].isin(valid_proficiencies).all():
        return None, f"Invalid 'user_proficiency_level'. Should be one of: {', '.join(valid_proficiencies)}"

    valid_impacts = ['Low', 'Medium', 'High', 'Critical']
    if not df['potential_impact'].isin(valid_impacts).all():
        return None, f"Invalid 'potential_impact'. Should be one of: {', '.join(valid_impacts)}"

    return df, ""


def validate_file_size(file, max_size: int) -> Tuple[bool, str]:
    """
    Validate the size of the uploaded file.

    Args:
    file: The uploaded file object
    max_size: Maximum allowed file size in bytes

    Returns:
    Tuple of (is_valid: bool, error_message: str)
    """
    if file.size > max_size:
        return False, f"File size exceeds the maximum limit of {max_size / (1024 * 1024):.2f} MB"
    return True, ""


def get_file_info(file) -> Dict[str, Any]:
    """
    Get information about the uploaded file.

    Args:
    file: The uploaded file object

    Returns:
    Dictionary containing file information
    """
    return {
        "name": file.name,
        "type": file.type,
        "size": file.size,
        "last_modified": pd.Timestamp(file.last_modified).isoformat() if hasattr(file, 'last_modified') else None
    }


# Example usage
if __name__ == "__main__":
    import streamlit as st

    st.title("File Upload and Processing Demo")

    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        file_info = get_file_info(uploaded_file)
        st.write("File Information:", file_info)

        is_valid_size, size_error = validate_file_size(uploaded_file, Config.MAX_UPLOAD_SIZE)
        if not is_valid_size:
            st.error(size_error)
        else:
            file_type = st.radio("Select file type:", ('KB Article', 'Ticket'))
            if st.button("Process File"):
                df, error = load_and_process_file(uploaded_file, file_type.lower().replace(" ", "_"))
                if error:
                    st.error(error)
                else:
                    st.success("File processed successfully!")
                    st.write(df.head())
