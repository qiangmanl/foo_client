#!/bin/bash

# Usage: ./get_ports.sh <keyword>
# Example: ./get_ports.sh clash
# Output: List of ports (space-separated) for processes matching the keyword

if [ $# -lt 1 ]; then
    echo "Usage: $0 <keyword>"
    exit 1
fi

KEYWORD=$1       # Process name or keyword to match
ports=()         # Array to store matched ports

# Iterate over lines matching the keyword in ss output
while read -r line; do
    # Extract local address field (usually 5th column)
    local_addr=$(echo "$line" | awk '{print $5}')
    # Get port number (after the last colon)
    port="${local_addr##*:}"
    # Only keep numeric ports
    if [[ "$port" =~ ^[0-9]+$ ]]; then
        ports+=("$port")
    fi
done < <(ss -tlup | grep "$KEYWORD")  # Match lines containing the keyword

# Print all matched ports
echo "${ports[@]}"
