import os
import requests
import time
from prometheus_client import start_http_server, Gauge
import yaml

# Fetch the base API URL from an environment variable
PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', '8000'))
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '30'))
PROMETHEUS_PREFIX = os.getenv('PROMETHEUS_PREFIX', 'powerloom')

print(f"""Starting with the following configuration:
PROMETHEUS_PORT={PROMETHEUS_PORT}
SCRAPE_INTERVAL={SCRAPE_INTERVAL}
PROMETHEUS_PREFIX={PROMETHEUS_PREFIX}""")

common_labels = [
    "api_url",
    "node"
]

status_metric_labels = [
    "status"
]

print("Loading config.yaml...", flush=True)

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

print("Fetching node URLs from config", flush=True)
nodes = config.get('nodes', [])
print(f"Found the following nodes:", flush=True)
for node in nodes:
    print(f"{node['name']} \t: {node['url']}", flush=True)

print("Creating epochId metric", flush=True)
# Define Prometheus Gauges (or Counters/Histograms depending on the use case)
epochId = Gauge(f'{PROMETHEUS_PREFIX}_epochId', 'Powerloom Epoch ID', common_labels)
status = Gauge(f'{PROMETHEUS_PREFIX}_status', 'Powerloom lite node status', common_labels + status_metric_labels)

# Function to fetch data for metric 1 and update the Gauge
def fetch_epochId(node):
    try:
        url = node['url']
        name = node['name']

        response = requests.get(f'{url}/current_epoch')
        response.raise_for_status()
        data = response.json()
        epoch_value = data.get('epochId', 0)

    except Exception as e:
        print(f"Error fetching epoch ID for node {name} at {url}: {e}", flush=True)
        epoch_value = 0
    epochId.labels(api_url=url, node=name).set(epoch_value)



# Function to fetch data for metric 1 and update the Gauge
def fetch_status(node):
    try:
        url = node['url']
        name = node['name']

        response = requests.get(f'{url}/health')
        response.raise_for_status()
        data = response.json()
        status_value = data.get('status', "ERROR")

    except Exception as e:
        print(f"Error fetching health status for node {name} at {url}: {e}", flush=True)
        status_value = "UNREACHABLE"

    node_statuses = {
        "UNREACHABLE":0,
        "ERROR":0,
        "OK":0
    }
    node_statuses[status] = 1

    for status_name, status_value in node_statuses.items():
        status.labels(api_url=url, node=name, status=status_name).set(status_value)




def main():
    # Start up the server to expose the metrics to Prometheus
    start_http_server(PROMETHEUS_PORT)  # Expose metrics on port 8000

    # Loop to fetch and update metrics periodically
    while True:
        print("Fetching data...", flush=True)
        for node in nodes:
            url = node['url']
            name = node['name']
            print(f"Fetching epochId for {name} at {url}", flush=True)
            fetch_epochId(node)  # Update epochId
            print(f"Fetching status for {name} at {url}", flush=True)

            fetch_status(node)
        print(f"Done, sleeping for {SCRAPE_INTERVAL} seconds...", flush=True)
        time.sleep(SCRAPE_INTERVAL)  # Scrape interval

if __name__ == "__main__":
    main()
