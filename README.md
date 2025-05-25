# Chi-Tan-Ga FastAPI Core

## Development Configurations

The file .app-env.local.dev is used when running the core standalone (not within docker compose)
The file .app-env.docker.dev is used when running the core within docker composer

## Running all locally with docker
The following command will start the chi-tan-ga-core and all dependent services:
```
docker compose --env-file .env.docker-compose run -e APP_ENV_FILE=.app-env.docker.dev chi-tan-ga-core
```

if you need rebuild Docker image of core:
```
docker compose --env-file .env.docker-compose up --build
```
## Running dependencies only with docker
This is useful for core debugging, to execute dependent services only, and start core in python debug mode.
```
docker compose --env-file .env.docker-compose up mqtt minio timescale
```

Run the app/main.py in whatever python debugger you like,
Don't forget to specify location of your application config:
```
APP_ENV_FILE=.app-env.local.dev
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

