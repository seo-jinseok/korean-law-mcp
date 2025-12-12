# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY .env.example .env

# Install dependencies and the package
# We install the current directory as a package
RUN pip install --no-cache-dir -e .

# Set environment variable placeholder (User should override this)
ENV OPEN_LAW_ID=your_id_here

# Run the server
CMD ["korean-law-mcp"]
