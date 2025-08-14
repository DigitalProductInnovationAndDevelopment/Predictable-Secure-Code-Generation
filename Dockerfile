# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    DEBIAN_FRONTEND=noninteractive

# --- 1️⃣  OS packages (compiler) ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# --- 2️⃣  Python dependencies ---
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# --- 3️⃣  Copy the Function code ---
COPY . /home/site/wwwroot

# -------- alias legacy import path --------
#  (adjust the right-hand side if the real package root is somewhere else)
RUN ln -s "/home/site/wwwroot/draft code/CodeFromRequirements" \
        /home/site/wwwroot/CodeFromRequirements