# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy project files to the container
COPY . /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y ffmpeg libopus0 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (useful for web apps)
EXPOSE 8080

# Run your script or bot (Replace with your main script)
CMD ["python", "your_main_script.py"]
