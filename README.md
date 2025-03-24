# Competitive Research Analysis API

This project is a FastAPI service that uses LangChain, ChatGroq, and SerpAPI to generate competitive research reports. The API accepts a list of competitors and a time period, then instructs an intelligent agent to gather and analyze relevant news. The final output is a detailed markdown report with strategic insights and recommendations.

## Features

- **Agent-Driven Analysis:** Uses a ChatGroq-based agent to perform multi-step reasoning and tool calls.
- **Real-Time Data Retrieval:** Leverages SerpAPI to fetch current news and updates.
- **External Prompt Templates:** All agent instructions are defined in external Jinja templates for easy customization.
- **Simple API Endpoint:** One endpoint to generate a full markdown report.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/competitive-research-api.git
   cd competitive-research-api
   ```

2. **Install Dependencies with Poetry:**

   Make sure you have [Poetry](https://python-poetry.org/) installed, then run:

   ```bash
   poetry install
   ```

3. **Set Up Environment Variables:**

   Create a `.env` file in the root directory with your API keys and settings:

   ```env
   GROQ_API_KEY=your_groq_api_key
   SERPAPI_API_KEY=your_serpapi_api_key
   ```

## Running the API

To start the FastAPI server locally:

```bash
poetry run uvicorn research:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Usage

### Generate a Report

- **Endpoint:** `POST /generate-report/`
- **Request Body Example:**

  ```json
  {
    "competitors": ["openai", "google"],
    "start_date": "2025-03-15T00:00:00",
    "end_date": "2025-03-24T00:00:00"
  }
  ```

- **Response Example:**

  ```json
  {
    "period": "2025-03-15 to 2025-03-24",
    "summary": "# Competitive Research Analysis Report\n\n... (markdown report)",
    "generated_at": "2025-03-24T20:00:00"
  }
  ```

## Customization

- **Prompt Template:**  
  Update the agent prompt in `templates/agent_prompt.jinja` to modify instructions for the agent.
  
- **Agent Configuration:**  
  Adjust the model name or parameters in `dependencies/research_agent.py` as needed.

## Contributing

Contributions are welcome. Feel free to open issues or submit pull requests with improvements.
