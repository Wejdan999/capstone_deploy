# Use an appropriate base image with CUDA support
FROM nvidia/cuda:12.1.0-runtime-ubuntu20.04

# Set the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt ./
RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the model file into the container
COPY "best (1).pt" ./

# Copy the rest of your application code
COPY . ./

# Expose the default Streamlit port
EXPOSE 8501

# Command to run your Streamlit app
CMD ["streamlit", "run", "dbds3.py", "--server.port=8501", "--server.address=0.0.0.0"]
