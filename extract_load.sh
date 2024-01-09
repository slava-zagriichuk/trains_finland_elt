#!/bin/bash

# Load the configuration file
config_file="config.txt"
if [ -f "$config_file" ]; then
    source "$config_file"
else
    echo "Error: Configuration file not found: $config_file"
    exit 1
fi


# Create folder if it doesn't exist function
create_folder () {
	local directory="$DESTINATION_FOLDER/$1"
	# Check if the directory exists
	if [ ! -d "$directory" ]; then
    	# Create the directory if it doesn't exist
    	mkdir -p "$directory"
    	echo "Directory created: $directory"
	else
    	echo "Directory already exists: $directory"
	fi
}


# Check directions file
file_directions_path="./directions.txt"
# Check if the file exists
if [ ! -f "$file_directions_path" ]; then
    echo "Error: File not found: $file_directions_path"
    exit 1
fi


# Define the current date
current_date=$(date +"%Y-%m-%d")


# Main Executive Script starts here

# Create log directory and file request_logs.txt if it's not exist
if [ ! -f "./logs/request_logs.txt" ]; then
	mkdir -p "./logs"
	touch "./logs/request_logs.txt"
fi

# Iteration of directions
while IFS= read -r item
do
	#create a folder for destination
    create_folder "$item"

    # Iteration of days forward from today
    for ((i=0; i<DAYS_FORWARD; i++))
    do
    	# Calculate the date i days in the future using the -v option (for macOS)
		# For Linux, you can use date -d "+i days" +"%Y-%m-%d"
		future_date=$(date -v+"$i"d +"%Y-%m-%d" 2>/dev/null || date -d "+"$i" days" +"%Y-%m-%d")
		# Do request and load to the file
    	./Utilities/request.sh $item $future_date >> "$DESTINATION_FOLDER/$item/$current_date.txt"
    done
done < "$file_directions_path"
