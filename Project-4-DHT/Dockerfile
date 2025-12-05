# use Python base image
FROM python:3.9-slim

# set working dir inside container
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY node.py .

# Expose port 5000
EXPOSE 5000

# run the app
CMD ["python", "node.py"]
