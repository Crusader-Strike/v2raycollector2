# V2Ray Config Collector

This script scrapes a list of public Telegram channels' web views in parallel to find and save V2Ray configuration links (vmess, vless, ss, hysteria). It uses multithreading to speed up the process.

## How to Use

### 1. Installation

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 2. Configuration

Open the `v2ray_collector.py` file and edit the `TELEGRAM_CHANNEL_NAMES` list to include the channel names you want to scrape.

For example:
```python
# A list of public Telegram channel names to scrape
TELEGRAM_CHANNEL_NAMES = [
    "V2rayCollector",
    "another_channel",
    # ... and so on
]
```

### 3. Running the Script

Execute the script from your terminal:

```bash
python v2ray_collector.py
```

### 4. Output

The script will create a directory named `v2ray_configs` in the same directory where the script is located. Inside this directory, it will create a single file for each protocol (`vmess.txt`, `vless.txt`, etc.). Each file contains all of the collected configs for that protocol, joined together by newlines. A `subscription.txt` file will also be generated containing a Base64 encoded V2Ray subscription link of all collected configs.

## Automation with GitHub Actions

This repository contains a GitHub Actions workflow to automatically run the script every hour and commit the updated configs.

To use it, simply push the `.github/workflows/v2ray_collector.yml` file to your GitHub repository. The action will be enabled and will start running on the defined schedule. You can also trigger it manually from the "Actions" tab in your repository.