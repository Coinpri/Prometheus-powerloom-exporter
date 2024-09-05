import os
import requests
import time
from prometheus_client import start_http_server, Gauge

# Fetch the base API URL from an environment variable
BASE_API_URL = os.getenv('BASE_API_URL')
PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', '8000'))
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '30'))
PROMETHEUS_PREFIX = os.getenv('PROMETHEUS_PREFIX', 'powerloom')

# Define Prometheus Gauges (or Counters/Histograms depending on the use case)
epochId = Gauge(f'{PROMETHEUS_PREFIX}_epochId', 'Powerloom Epoch ID')

# Function to fetch data for metric 1 and update the Gauge
def fetch_epochId():
    try:
        response = requests.get(f'{BASE_API_URL}/current_epoch')
        response.raise_for_status()
        data = response.json()
        value1 = data.get('epochId', 0)
        # Update Prometheus metric
        epochId.set(value1)
    except Exception as e:
        print(f"Error fetching metric 1: {e}")


def main():
    # Start up the server to expose the metrics to Prometheus
    start_http_server(PROMETHEUS_PORT)  # Expose metrics on port 8000

    # Loop to fetch and update metrics periodically
    while True:
        fetch_epochId()  # Update epochId
        time.sleep(30)  # Scrape interval

if __name__ == "__main__":
    main()
