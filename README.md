# BioFieldResearchAgent FastAPI Backend

## Running all locally with docker
```
APP_ENV_FILE=.env.dev
docker compose --env-file .env.compose up
```
## Debugging backend and running dependencies only with docker

```
docker compose --env-file .env.compose up mqtt minio timescale
```

Run the app/main.py in whatever python debugger you like,
Dont forget to specify location of your application config:
```
APP_ENV_FILE=.env.dev
```

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [OpenAI API](https://openai.com/) (API key for LLM processing)
- Required Python packages (install using the command below)

---
## Contributing
Contributions are welcome! Feel free to:
- Report issues via GitHub Issues
- Submit feature requests
- Fork the repo and create pull requests

---
## License
This project is licensed under the [MIT LICENSE](https://mit-license.org/).

