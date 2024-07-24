# KB Article and Ticket Processing System

## Overview

This application is a Knowledge Base (KB) Article and Ticket Processing System designed to manage, analyze, and visualize KB articles and support tickets. It leverages Azure Cosmos DB for storage and OpenAI's text embedding model for advanced text processing and similarity searches.

## Features

- Upload and process KB articles and support tickets
- Generate and manage text embeddings for advanced search capabilities
- Visualize data with interactive charts and graphs
- Search for similar KB articles and tickets based on content
- Dashboard for viewing statistics and data insights

## Tech Stack

- Python 3.x
- Streamlit for the user interface
- Azure Cosmos DB for data storage
- OpenAI API for text embeddings
- Plotly for data visualization
- Pandas for data manipulation

## Project Structure

```
.
├── app.py                  # Main application entry point
├── app/
│   ├── config.py           # Configuration settings
│   ├── core/               # Core application logic
│   │   ├── article_processor.py
│   │   ├── cosmos_db_manager.py
│   │   └── embedding_manager.py
│   ├── ui/                 # User interface components
│   │   ├── main_view.py
│   │   ├── dashboard_view.py
│   │   └── search_view.py
│   └── utils/              # Utility functions
│       ├── file_handler.py
│       ├── visualization.py
│       └── utils.py
└── requirements.txt        # Project dependencies
```

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/kb-ticket-processing-system.git
   cd kb-ticket-processing-system
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   COSMOS_ENDPOINT=your_cosmos_db_endpoint
   COSMOS_KEY=your_cosmos_db_key
   OPENAI_API_KEY=your_openai_api_key
   ```

## Running the Application

To run the application, use the following command:

```
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

## Usage

1. **Upload Data**: Use the "Upload and Process" page to upload KB articles or support tickets.
2. **Search**: Navigate to the "Search" page to find similar KB articles or tickets based on your query.
3. **Dashboard**: View statistics and visualizations on the "Dashboard" page.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
