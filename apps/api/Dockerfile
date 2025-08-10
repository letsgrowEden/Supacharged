# Stage 1: Build Stage - Install dependencies using uv
FROM python:3.12-slim as builder

# Install uv, the fast Python package manager
RUN pip install uv

WORKDIR /app

# Copy only the dependency definition files
COPY pyproject.toml uv.lock* ./

# Install dependencies into a virtual environment managed by uv
# This creates a cached layer that only changes when dependencies do
RUN uv pip install --system --no-cache -r pyproject.toml

# Stage 2: Final Stage - Run the application
FROM python:3.12-slim

WORKDIR /app

# Copy the virtual environment with installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENV PYTHONPATH=/app/src

# Copy our application code
COPY ./src ./src

# Expose the port the app will run on
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
