FROM python:3.9-slim

# create application folder and install environment
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# copy accounts service package
COPY service/ ./service/

# run as non-root user
RUN useradd --uid 1000 theia && chown -R theia /app
USER theia

# start service
EXPOSE 8080
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--log-level=info", "service:app"]
