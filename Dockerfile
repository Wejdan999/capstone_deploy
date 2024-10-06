# Use an appropriate base image
FROM nvidia/cuda:12.1.0-runtime-ubuntu20.04

# Set the working directory in the container
WORKDIR /app

# Install necessary libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the model file into the container
COPY "best (1).pt" ./ 

# Copy the rest of your application code
COPY . ./ 

# Command to run your Streamlit app
CMD ["streamlit", "run", "dbds3.py"]
