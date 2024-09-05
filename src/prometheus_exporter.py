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
    "api_url"
]

print("Loading config.yaml...", flush=True)

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

print("Fetching node URLs from config", flush=True)
node_urls = config.get('node_urls', [])
print(f"Found the following node URLs:", flush=True)
for url in node_urls:
    print(url, flush=True)

print("Creating epochId metric", flush=True)
# Define Prometheus Gauges (or Counters/Histograms depending on the use case)
epochId = Gauge(f'{PROMETHEUS_PREFIX}_epochId', 'Powerloom Epoch ID', common_labels)

# Function to fetch data for metric 1 and update the Gauge
def fetch_epochId(url: str):
    try:
        response = requests.get(f'{url}/current_epoch')
        response.raise_for_status()
        data = response.json()
        value1 = data.get('epochId', 0)
        # Update Prometheus metric
        epochId.labels(api_url=url).set(value1)
    except Exception as e:
        print(f"Error fetching epoch ID for URL {url}: {e}", flush=True)


def main():
    # Start up the server to expose the metrics to Prometheus
    start_http_server(PROMETHEUS_PORT)  # Expose metrics on port 8000

    # Loop to fetch and update metrics periodically
    while True:
        print("Fetching data...", flush=True)
        for url in node_urls:
            print(f"Fetching epochId for {url}", flush=True)
            fetch_epochId(url)  # Update epochId
            print(f"Done, sleeping for {SCRAPE_INTERVAL} seconds...", flush=True)
        time.sleep(SCRAPE_INTERVAL)  # Scrape interval

if __name__ == "__main__":
    main()
