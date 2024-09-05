# Weather Impacts and Outage Prediction Using Distribution Networks' Topology and Physical Features

This project aims to predict power outages by analyzing the topology of distribution networks and their physical features, in combination with weather data. The project utilizes several APIs to retrieve relevant data and implements a Command Line Interface (CLI) for ease of use.

## Authors

- Kenneth McDonald
- Colin T. Le
- Zhihua Qu

## Setup

To get the CLI running, first install the package in editable mode:

```bash
pip install --editable .
```

## CLI Commands

### 1. Import DSS Files
Process DSS files and save nodeList and edgeList as CSV files.

**Options:**
- `--input-path PATH`: Relative path to the input directory containing the DSS files.
- `--output-path PATH`: Directory where the nodeList & edgelist CSV files will be saved.

### 2. Get Weather Events
Retrieve weather events for a specified state, events, and date range, and save the result as a CSV file.

**Options:**
- `--state`: Full name (e.g., Florida, Georgia).
- `--events`: One or more events (see list of possible events below).
- `--nodelist PATH`: Relative path to the nodelist CSV file.
- `--start-date TEXT`: Start date in YYYY-MM-DD format.
- `--end-date TEXT`: End date in YYYY-MM-DD format.
- `--output-path PATH`: Relative path to save the output CSV file.

### Possible Weather Events
- Astronomical Low Tide
- Avalanche
- Blizzard
- Coastal Flood
- Cold/Wind Chill
- Debris Flow
- Dense Fog
- ... (and more)

### 3. Format Weather Data
Find weather features that occurred at each node and edge in the network based on weather events.

**Options:**
- `--events-file PATH`: Path to the CSV file containing weather events.
- `--nodelist PATH`: Path to the CSV file containing the nodelist.
- `--output-path PATH`: Relative output path to save the results.
- `--features`: Weather features to process [temp dwpt rhum prcp snow wdir wspd wpgt pres tsun coco].

### 4. Generate Weather Impact
Generate weather impact based on input features, node, and edge data.

**Options:**
- `--feature-list <TEXT INTEGER INTEGER>`: List of features with min and max values. Example: `--feature-list temp 0 100`.
- `--input-path PATH`: Input relative path to the folder containing the feature folders.
- `--node-feature <TEXT FLOAT FLOAT>`: Node feature with relative values. Example: `elevation 0.5 0.5`.
- `--edge-feature <TEXT FLOAT FLOAT>`: Edge feature with relative values. Example: `elevation 0.7 0.3`.
- `--output-path PATH`: Output directory to save the results.

### 5. Generate Outage Map
Generate an outage map using specified node and edge features and weather impacts.

**Options:**
- `--node-feature <TEXT FLOAT FLOAT FLOAT FLOAT>`: Node feature with mean min, mean max, std min, and std max. Example: `elevation 0.5 1.0 0.1 0.2`.
- `--edge-feature <TEXT FLOAT FLOAT FLOAT FLOAT>`: Edge feature with mean min, mean max, std min, and std max. Example: `length 0.7 0.9 0.2 0.3`.
- `--list-folder PATH`: Input relative path to the folder containing `nodeList.csv` and `edgeList.csv`.
- `--wi-folder PATH`: Input relative path to the folder containing weather impacts. This folder should contain “edges” and “nodes” folders.

## Data Sources

- **USGS 3DEP**
- **NLCD**
- **SMART-DS**
- **SINGOther Synthetic Network Generators**
- **NLDAS2**
- **MeteoStat**
