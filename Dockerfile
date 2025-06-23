FROM python:3.9

WORKDIR /app

# Install uv
RUN pip install uv

# Copy deps + lockfile first to cache layers
COPY requirements.txt /app/

# Install dependencies
RUN uv venv
RUN uv pip install -r requirements.txt --system

COPY flask-app /app/flask-app
COPY agentd /app/agentd

EXPOSE 8080

# Start your app
CMD ["gunicorn", "-b", "0.0.0.0:8080", "flask-app.app:app"]
