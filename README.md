# Plural

Adaptive Persona Management

## Getting Started

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

Run the server with:

```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## Using Docker

You can also run the application using Docker:

1. Build and start the container:
   ```bash
   docker-compose up --build
   ```

2. The application will be available at `http://127.0.0.1:8000`.

## Documentation

Once the app is running, you can verify it by visiting:
- [http://127.0.0.1:8000/](http://127.0.0.1:8000/) - Hello World response
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) - Swagger UI documentation
