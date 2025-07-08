FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make scripts executable
RUN chmod +x seed_database.py run_local.py

# Expose the port
EXPOSE 8001

# Run the application
CMD ["python", "main.py"] 