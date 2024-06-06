#!/bin/bash

SECONDS=0

# Database credentials
username='papadomalake'
password='mamamialetmego'
host='pharmcon.mysql.tools'
port='3306'
database='pharmcon_lake'

# Test the connection
mysql -u $username -p$password -h $host -P $port -e "USE $database;" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Connection failed!"
    exit 1
else
    echo "Connection successful!"
fi

# Define the function to get the link via wget
get() {
    link=$1
    wget "$link" -O page_parent.html
}

# Fetch the main page and parse it
wget "https://www.wassertemperatur.org/tegernsee/" -O page.html
SeeLinks=($(grep -oP 'href="\K[^"]*Wassertemperatur[^"]*(?=")' page.html))
#LakeNames=($(grep -oP 'Wassertemperatur \K[^<]*' page.html))
LakeNames=($(grep -oP '>Wassertemperatur \K[^<]*(?=</a>)' page.html))
#LakeNames=($(grep -oP '(?<=<h1 class="entry-title">Wassertemperatur )[^<]+' page.html))

# Combine links and lake names into an array of strings
declare -a SeeLinksArray
for ((i=0; i<${#SeeLinks[@]}; i++)); do
    SeeLinksArray+=("${SeeLinks[$i]}|${LakeNames[$i]}")
done

# Output the found links and lake names
echo "Total Lakes number is: ${#SeeLinksArray[@]}"

# Progress bar initialization
total=${#SeeLinksArray[@]}
current=0

# Iterate over the links and fetch temperature data
for entry in "${SeeLinksArray[@]}"; do
    link=${entry%|*}
    lake=${entry#*|}
    get "$link"
    temperature=$(grep -oP '<span[^>]*>(?:<span[^>]*>)?\K\d+(?=\s*°C<\/span>)' page_parent.html | head -1)
    if [ -n "$temperature" ]; then
        echo "Temp FOUND! in $entry at $temperature"
        SeeLinksArray[$current]="$link|$lake|$temperature"
    fi

    # Update progress bar
    ((current++))
    echo -ne "Progress: $current/$total\r"
done

echo "Raw SeeLinks: ${SeeLinksArray[@]}"

# Prepare data for SQL insertion
declare -a ValuesList
for entry in "${SeeLinksArray[@]}"; do
    parts=(${entry//|/ })
    if [ ${#parts[@]} -eq 3 ]; then
        ValuesList+=("('${parts[0]}', '${parts[1]}', ${parts[2]})")
    fi
done

# Create SQL insert statement
values_str=$(IFS=,; echo "${ValuesList[*]}")
stmt="INSERT INTO bavarianlakes (link, lake, temp) VALUES $values_str;"

# Execute the SQL statement
mysql -u $username -p$password -h $host -P $port -D $database -e "$stmt"

echo "Data inserted successfully!"
duration=$SECONDS
echo "$((duration / 60)) minutes and $((duration % 60)) seconds elapsed."
