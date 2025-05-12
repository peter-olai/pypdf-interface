# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install any needed packages specified in requirements.txt
# Ensure you have a requirements.txt file that includes Flask and pypdf
# For example, your requirements.txt could contain:
# Flask>=2.0
# pypdf>=3.0
RUN pip install --no-cache-dir Flask pypdf

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
