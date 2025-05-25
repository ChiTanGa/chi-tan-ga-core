# Chi-Tan-Ga FastAPI Core

## Development Configurations

The file .app-env.local.dev is used when running the core standalone (not within docker compose)
The file .app-env.docker.dev is used when running the core within docker composer

## Running all locally with docker
```
docker compose --env-file .env.docker-compose up
```
if you need rebuild Docker image of core:
```
docker compose --env-file .env.docker-compose up --build
```
Note that the application environment variable file is linked inside of .env.compose file -> APP_ENV_FILE=.env.dev
## Running dependencies only with docker
This is useful for core debugging
```
docker compose --env-file .env.docker-compose up mqtt minio timescale
```

Run the app/main.py in whatever python debugger you like,
Don't forget to specify location of your application config:
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

