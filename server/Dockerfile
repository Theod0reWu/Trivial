# Start from a base image
FROM python:3.12.3
ENV FIREBASE_PATH gen-lang-client-0263701804-firebase-adminsdk-rjr2c-e90c9bfb5a.json


# Set the working directory
WORKDIR ./app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the required packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Expose the app port
EXPOSE 8080

# Run command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]