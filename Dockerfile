# First stage: build stage
FROM python:3.13-slim AS builder

# Install binutils
RUN apt-get update && apt-get install -y binutils

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./flask_app /app/

# Install any needed dependencies specified in requirements.txt
COPY ./flask_app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Build the executable
RUN pyinstaller \
    --distpath dist \
    --workpath build \
    --specpath . \
    --clean \
    --onedir \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --hidden-import config \
    --hidden-import routes \
    app.py

# Second stage: runtime stage
FROM python:3.13-slim

WORKDIR /app

# Copy the database file from the builder stage
COPY --from=builder /app/database_file /app/database_file
# Copy the executable from the builder stage
COPY --from=builder /app/dist/app /app

COPY --from=builder /app/image_pool /app/image_pool

# Expose the port the app runs on
EXPOSE 5000

ENTRYPOINT [ "./app" ]