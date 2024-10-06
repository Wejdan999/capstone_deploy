# Use an appropriate base image with Ubuntu and CUDA
FROM nvidia/cuda:12.1.0-runtime-ubuntu20.04

# Install Python, pip, and other necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libgl1-mesa-glx \  # This is the library that provides libGL.so.1
    libglib2.0-0 \      # Additional library that may be needed
    && apt-get clean

# Upgrade pip
RUN pip3 install --upgrade pip

# Set the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the model file into the container
COPY best_model.pt ./

# Copy the rest of your application code
COPY . ./

# Command to run your Streamlit app
CMD ["streamlit", "run", "dbds3.py"]
