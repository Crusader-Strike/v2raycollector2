# ===== IMPORTS & DEPENDENCIES =====
import requests
import concurrent.futures
import logging
import re
import base64
from pathlib import Path
from typing import List, Set, Dict, Optional
from bs4 import BeautifulSoup

# ===== CONFIGURATION & CONSTANTS =====
# Directory to save the output files
OUTPUT_DIR = Path("v2ray_configs")
# File containing the list of Telegram channel names, one per line
CHANNELS_FILE = Path("channels.txt")
# User-Agent header for HTTP requests to mimic a browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# V2Ray protocols to search for
PROTOCOLS = {"vmess", "vless", "ss", "trojan", "hysteria", "hy2"}
# Request timeout in seconds
REQUEST_TIMEOUT = 10

# ===== LOGGING SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ===== CORE LOGIC & UTILITY FUNCTIONS =====

def load_channels(file_path: Path) -> List[str]:
    """
    Loads Telegram channel names from a text file.

    Args:
        file_path: The path to the file containing channel names.

    Returns:
        A list of channel names. Skips empty lines and lines starting with '#'.
    """
    if not file_path.exists():
        logging.error(f"Channels file not found at: {file_path}")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        channels = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]
    logging.info(f"Loaded {len(channels)} channels from {file_path}")
    return channels

def fetch_channel_content(session: requests.Session, channel_name: str) -> Optional[str]:
    """
    Fetches the HTML content of a public Telegram channel's web view.

    Args:
        session: The requests session object.
        channel_name: The name of the Telegram channel.

    Returns:
        The HTML content as a string, or None if an error occurs.
    """
    url = f"https://t.me/s/{channel_name}"
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch content for channel '{channel_name}': {e}")
        return None

def parse_v2ray_configs(html_content: str) -> Set[str]:
    """
    Parses HTML content to find and extract V2Ray configuration links.

    Args:
        html_content: The HTML content of the Telegram page.

    Returns:
        A set of unique V2Ray config strings found on the page.
    """
    configs: Set[str] = set()
    soup = BeautifulSoup(html_content, "html.parser")
    # Regex to find any of the specified protocols at the start of a string
    protocol_pattern = re.compile(r"^(vmess|vless|ss|trojan|hysteria|hy2)://")

    # Find all <code> blocks, which commonly contain configs
    for code_block in soup.find_all("code"):
        text = code_block.get_text(separator="\n").strip()
        # Split by lines and check each line
        for line in text.splitlines():
            clean_line = line.strip()
            if protocol_pattern.match(clean_line):
                configs.add(clean_line)
    
    return configs

def scrape_channel(session: requests.Session, channel_name: str) -> Set[str]:
    """
    Scrapes a single Telegram channel and returns a set of unique configs.

    Args:
        session: The requests session object.
        channel_name: The name of the Telegram channel to scrape.

    Returns:
        A set of unique V2Ray configs found, or an empty set if none are found or an error occurs.
    """
    logging.info(f"Scraping channel: {channel_name}")
    html_content = fetch_channel_content(session, channel_name)
    if not html_content:
        return set()

    configs = parse_v2ray_configs(html_content)
    if configs:
        logging.info(f"Found {len(configs)} configs in channel: {channel_name}")
    return configs

def save_configs_to_files(configs: List[str]):
    """
    Saves the extracted configs into separate files based on their protocol.

    Args:
        configs: A list of unique V2Ray config strings.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Group configs by protocol
    grouped_configs: Dict[str, List[str]] = {
        "vmess": [], "vless": [], "ss": [], "trojan": [], "hysteria": []
    }

    for config in configs:
        protocol_match = re.match(r"(\w+):?//", config)
        if protocol_match:
            protocol = protocol_match.group(1).lower()
            # Unify hysteria variants under a single key
            if protocol in ["hysteria2", "hy2"]:
                protocol = "hysteria"
            
            if protocol in grouped_configs:
                grouped_configs[protocol].append(config)

    # Save each protocol's configs to a file
    for protocol, config_list in grouped_configs.items():
        if config_list:
            file_path = OUTPUT_DIR / f"{protocol}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(config_list))
            logging.info(f"Saved {len(config_list)} {protocol} configs to {file_path}")

def generate_subscription_file(configs: List[str]):
    """
    Generates a Base64 encoded V2Ray subscription file.

    Args:
        configs: A list of all unique config strings.
    """
    if not configs:
        return

    subscription_content = "\n".join(configs)
    encoded_content = base64.b64encode(subscription_content.encode("utf-8")).decode("utf-8")
    
    subscription_file_path = OUTPUT_DIR / "subscription.txt"
    with open(subscription_file_path, "w", encoding="utf-8") as f:
        f.write(encoded_content)
    logging.info(f"Generated V2Ray subscription link and saved to {subscription_file_path}")
    
# ===== INITIALIZATION & STARTUP =====

def main():
    """The main function to orchestrate the scraping process."""
    channels = load_channels(CHANNELS_FILE)
    if not channels:
        logging.warning("No channels to scrape. Exiting.")
        return

    all_configs: Set[str] = set()
    
    # Use a session object for connection pooling
    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})
        # Use ThreadPoolExecutor for parallel scraping
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Map the scrape_channel function to the list of channel names
            future_to_channel = {executor.submit(scrape_channel, session, name): name for name in channels}
            for future in concurrent.futures.as_completed(future_to_channel):
                try:
                    channel_configs = future.result()
                    all_configs.update(channel_configs)
                except Exception as e:
                    channel_name = future_to_channel[future]
                    logging.error(f"An exception occurred while processing channel {channel_name}: {e}")

    if all_configs:
        unique_configs = sorted(list(all_configs))
        logging.info(f"\n--- Scraping Complete ---")
        logging.info(f"Found a total of {len(unique_configs)} unique V2Ray configs.")
        
        save_configs_to_files(unique_configs)
        generate_subscription_file(unique_configs)
    else:
        logging.info("\n--- Scraping Complete ---")
        logging.info("No V2Ray configs were found across any of the channels.")


if __name__ == "__main__":
    main()