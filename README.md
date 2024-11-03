# Airbnb Listings Viewer

This Streamlit application connects to a MongoDB database containing Airbnb rental data and provides a user-friendly interface to view, filter, and analyze the listings and their reviews. The app also includes functionality to add new reviews and generate AI-powered review summaries.

## Features
- View and filter Airbnb listings
- Display detailed information about selected listings
- Add new reviews to listings
- Generate AI summaries for reviews

## Prerequisites
- Python 3.7 or higher
- Streamlit
- MongoDB Atlas account: https://www.mongodb.com/docs/atlas/getting-started/
- OpenAI API key: https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/mongodb-developer/stream-airbnb-ai-reviews.git
    cd stream-airbnb-ai-reviews
    ```

2. Install the required packages:
     ```bash
     pip install -r requirements.txt
     ```

3. Set up environment variables:
    - `MONGODB_ATLAS_URI`: Your MongoDB Atlas connection string
    - `OPENAI_API_KEY`: Your OpenAI API key

    You can create a `.env` file in the root directory and add the following:
     ```env
     MONGODB_ATLAS_URI=your_mongodb_atlas_uri
     OPENAI_API_KEY=your_openai_api_key
     ```
4. Ingest data using Hugging Face free token from [airbnb hugging face data set](https://huggingface.co/datasets/MongoDB/airbnb_embeddings):
```bash
huggingface-cli login 
python ingest.py
```

4. Run the Streamlit app:
     ```bash
     streamlit run app.py
     ```

You should be able to now operate the UI and add reviews and generate AI based reviews.

## Issue fixing

### Issue 1 - ValueError: Invalid pattern: '**' can only be an entire path component

```bash
python -m pip install datasets
```

### Issue 2 - pymongo.errors.ServerSelectionTimeoutError

Symptoms:

```Bash
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [Errno 61] Connection refused (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 30s, Topology Description: <TopologyDescription id: 6726cc62646f15c803d027b5, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [Errno 61] Connection refused (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
```

Root Cause:

The connection between db and app is broken.