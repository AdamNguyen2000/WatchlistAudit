
# Watchlist Audit Tool

## Overview

This Python script is designed to optimize and maintain the efficiency of Microsoft Sentinel watchlists by identifying unused watchlist names. The script checks the usage of each watchlist name in detection files (`.yaml` and `.json`) and cross-verifies them with log data using Azure Monitor API. The tool reduces noise in alerting systems by focusing on high-risk items while identifying redundant entries.

## Features

- **Cross-match watchlist names with detection files:** Identifies which watchlist names are used in `.yaml` or `.json` detection files.
- **Query unused watchlist names in Azure logs:** Formats and queries unused watchlist names to check their recent occurrences in log data.
- **Interactive Azure authentication:** Uses the Azure InteractiveBrowserCredential for secure and seamless account access.
- **Detailed outputs:** Provides insights into watchlist usage, unused entries, and query results in an organized format.

## Prerequisites

- Python 3.x installed
- Azure account with necessary permissions
- Watchlist names stored in a file named `watchlist.txt` in the same directory as the script
- Access to the Microsoft Sentinel Log Analytics Workspace

## Installation

1. Clone the repository:
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2. Install required Python packages:
    ```bash
    pip install azure-identity azure-monitor-query
    ```

3. Ensure `watchlist.txt` is populated with all the watchlist names, one per line.

## Usage

1. Run the script using the following command:
    ```bash
    python3 wlaudit.py <target_directory>
    ```

    - `<target_directory>`: The directory containing the `.yaml` and `.json` detection files.

2. The script performs the following tasks:
    - Reads all watchlist names from `watchlist.txt`.
    - Searches for watchlist names in `.yaml` and `.json` files within the specified directory.
    - Outputs the usage of each watchlist name and the files where they are found.
    - Formats unused watchlist names into a query and checks their presence in Azure logs.

3. Log in to Azure when prompted to execute the log query.

## Outputs

- **CSV Format:** Outputs each watchlist name, its usage status, and the corresponding detection files.
- **KQL Query:** Generates a formatted KQL query for unused watchlist names.
- **Azure Query Results:** Prints the rows returned by the Azure Monitor query.

## Example

### Command:
```bash
python3 wlaudit.py /path/to/detection/files
```

### Output:
```
Watchlist, Used, Files
Item1, True, /path/to/file1.yaml
Item2, False, 
...
```

### Generated Query:
```kql
LAQueryLogs
| where TimeGenerated >= ago(90d)
| where QueryText has_any ("Name1", "Name2")
| extend Watchlist = extract(@'_GetWatchlist\((\S+)\)',1, QueryText)
| distinct Watchlist
```
