#!/bin/bash

# Check the number of arguments
if [ "$#" -lt 3 ]; then
    echo "Error: Insufficient number of arguments. Please provide three arguments."
    exit 1
fi

# Accessing command line arguments
departure=$1
arrival=$2
dep_date=$3

# log file address
log_file="./logs/request_logs.txt"

# API endpoint URL
url="https://www.vr.fi/api/v7"

# JSON payload
payload=$(sed "s/{{ARRIVAL_STATION}}/"$arrival"/1; s/{{DEPARTURE_STATION}}/"$departure"/1; s/{{DATE}}/"$dep_date"/1" "./Resources/payload.json")

# Make the POST request
response=$(curl -s -w "Status Code: %{http_code}, Time to Connect: %{time_connect}, Bytes Downloaded: %{size_download}\n" -X POST -H "Content-Type: application/json" -d "$payload" "$url")

# Extract content and status code from the response
content=$(echo "$response" | sed -n '1p')
parameters=$(echo "$response" | sed -n '2p')

# Log the request
echo "[$(date +"%Y-%m-%d %H:%M:%S")] $departure, $arrival, $dep_date, $parameters" >> "$log_file"

# Return the content
echo "$content"