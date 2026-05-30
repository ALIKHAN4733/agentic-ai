# Use slim Python 3.13 (same as your local version)
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy only requirements first → better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# Copy your agent code
COPY agent.py .

# We'll override .env at runtime for security (never commit secrets!)
COPY .env .

# Use non-root user (good security practice)
RUN useradd -m appuser
USER appuser

# Expose port (informational - agent uses dynamic ports)
EXPOSE 8080

# Run the agent in production mode
CMD ["python", "agent.py", "start"]