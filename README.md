# lelapa-demos-unitech

This project provides an API for querying Eskom FAQs in English.

## Overview

lelapa-demos-unitech is a FastAPI-based application that allows users to query Eskom FAQs through a simple API interface. It uses PDM for dependency management and includes a scraper for collecting FAQ data.

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/Lelapa-AI/lelapa-demos-unitech.git
   cd lelapa-demos-unitech
   ```

2. Install PDM if you haven't already:
   ```
   pip install pdm
   ```

3. Install dependencies:
   ```
   pdm install
   ```

4. Run the script to collect FAQ data from Eskom Website:
   ```
   cd src/lelapa_demos_unitech/
   pdm run data
   ```

5. Start the API:
   ```
   pdm run start
   ```

## Usage

To use the API, send a POST request to the `/faq` endpoint with a JSON body containing your question. For example:

```bash
curl -X POST http://localhost:8000/faq \
     -H "Content-Type: application/json" \
     -d '{"question": "How do I get prepayment electricity?"}'
```

## Environment Variables

Create a `.env` file in the root directory of the project with the following variables:

```
VULAVULA_API_TOKEN=your_vulavula_api_token
FAQ_FILE_PATH=/path/to/your/faq/file
```

- `VULAVULA_API_TOKEN`: Your API token for the VulaVula service.
- `EMFULENI_FAQ_FILE_PATH`: The path to the FAQ file from eskom used by the application.
- `ESKOM_FAQ_FILE_PATH`: The path to the FAQ file from emfuleni used by the application.

Replace `your_vulavula_api_token` and `/path/to/your/faq/file` with your actual values.

## Running with Docker

### Build the Docker Image

From the project's root directory:

```bash
docker build -t lelapa-demos-unitech .
```

### Run the Docker Container

```bash
docker run --env-file .env -p 8000:8000 lelapa-demos-unitech
```

This command loads environment variables from the `.env` file and maps port 8000 of the container to port 8000 on your host machine.

### Access the Application

Once the container is running, access the FastAPI application at [http://localhost:8000](http://localhost:8000).

## Development

For local development without Docker:

1. Install dependencies:
   ```bash
   pdm install
   ```

2. Run the application:
   ```bash
   pdm run start
   ```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).

