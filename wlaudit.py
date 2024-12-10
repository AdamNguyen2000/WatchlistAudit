import os
import re
import sys  
from azure.identity import InteractiveBrowserCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from datetime import timedelta

# File paths
watchlist_file_path = "watchlist.txt"  # Path to the watchlist file which is ALL names

# Read the watchlist.txt file and store all names in a list named watchlist
with open(watchlist_file_path, 'r') as watchlist_file:
    watchlist = [line.strip() for line in watchlist_file if line.strip()]

# Function to search for watchlist names in a given file (YAML or JSON)
def check_wl_in_file(file_path, wl_list):
    matched_wl = []  # List to store detected matches from the watchlist
    with open(file_path, 'r') as file:
        content = file.read()  # Read the entire file content
        # Loop through the watchlist to find occurrences in the file
        for Detections in wl_list:
            # Regular expression pattern to match GetWatchlist('Name') or GetWatchlist("Name")
            pattern = f'GetWatchlist\\(["\']{Detections}["\']\\)'
            if re.search(pattern, content, re.IGNORECASE):  # Perform a case-insensitive search
                matched_wl.append(Detections)  # Add to the list if a match is found
    return matched_wl

# Ensure the script is called with a target directory path
if len(sys.argv) != 2:
    print("Usage: python3 wlaudit.py <target_directory>")
    sys.exit(1)

# Set target directory from script argument
target_directory = sys.argv[1]

# Dictionary to track which watchlist names are used and their corresponding files
watchlist_usage = {item: {"Used": False, "Files": []} for item in watchlist}

# Recursively walk through the directory to process each file
for root, dirs, files in os.walk(target_directory):
    for file in files:
        # Only process .yaml and .json files
        if file.endswith((".yaml", ".json")):
            file_path = os.path.join(root, file)
            matches = check_wl_in_file(file_path, watchlist)  # Check for watchlist matches
            for match in matches:
                watchlist_usage[match]["Used"] = True
                watchlist_usage[match]["Files"].append(file_path)

# Print the watchlist usage as CSV
print("Watchlist, Used, Files")
for item, details in watchlist_usage.items():
    used_status = "True" if details["Used"] else "False"
    files_list = ";".join(details["Files"]) if details["Files"] else ""
    print(f"{item}, {used_status}, {files_list}")

# Collect all watchlist names that are marked as 'False' and format them
false_watchlists = [item for item, details in watchlist_usage.items() if not details["Used"]]

# Generate and print the formatted query if there are any false watchlists
if false_watchlists:
    formatted_false_watchlists = '", "'.join([name for name in false_watchlists])
    query = f"""
LAQueryLogs
| where TimeGenerated >= ago(90d)
| where QueryText has_any ("{formatted_false_watchlists}")
| extend Watchlist = extract(@'_GetWatchlist\\((\\S+)\\)',1, QueryText)
| distinct Watchlist
"""
    print(query)

    # Azure Authentication and Query Execution

    # Use InteractiveBrowserCredential
    credential = InteractiveBrowserCredential()

    # Create a client for querying logs
    client = LogsQueryClient(credential)

    # Replace with your Log Analytics Workspace ID
    workspace_id = 'insert workspace id here'

    # Correct usage of timespan
    timespan = timedelta(days=90)  # Time range for the query (last 1 hour)

    # Execute the query against Azure Monitor
    try:
        response = client.query_workspace(workspace_id, query, timespan=timespan)
        
        # Check for the query result status and print the result if successful
        if response.status == LogsQueryStatus.SUCCESS:
            print("Query Succeeded! Results:")

            # Iterate over the tables and rows in the response to print the results
            for table in response.tables:
                if table.rows:
                    print(f"Row count: {len(table.rows)}")
                    for row in table.rows:
                        # Remove trailing quotes and parentheses
                        cleaned_row = re.sub(r"[\"')]+$", "", row[0])  # Remove trailing quotes and parentheses
                        cleaned_row = cleaned_row.strip('\'"')        # Strip leading quotes
                        print(cleaned_row)
                else:
                    print("No data returned for the table.")
        else:
            print("Query failed.")
    except Exception as e:
        print(f"Error executing query: {e}")
else:
    print("\nAll watchlist items are marked 'True'.")
