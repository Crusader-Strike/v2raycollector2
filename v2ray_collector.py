# v2ray_collector.py
# This script will scrape a Telegram channel for V2Ray configs.
import requests
from bs4 import BeautifulSoup
import os
import re
import concurrent.futures
import subprocess
import json
import time
import tempfile
import urllib.parse
import base64

# --- CONFIGURATION ---
# A list of public Telegram channel names to scrape
TELEGRAM_CHANNEL_NAMES = [
    "ablnet7", "abrivpn", "academi_vpn", "ae_proxy", "ai_duet", "aklisvpn", 
    "alfa_v2ray_ng", "alfred_config", "alo_v2rayng", "am20094", "amirw_shop_q", 
    "antimeli", "anty_vpn", "arv2ray", "asak_vpn", "asrnovin_ir", "astrovpn_official", 
    "ata_connect", "atovpn", "awlix_ir", "aymh19", "azadiiivpn", "azadmarz", 
    "azadnett1", "azarandoozvpn", "bad_raqs", "banv2ray", "befreewithus", "binextify", 
    "bluev2rayng", "bluvpnir", "bolbolvpn", "bored_vpn", "bypass_filter", "canfigvip", 
    "capoit", "catvpns", "cav2ray", "colsvpn", "config_on", "config_proxy", 
    "config_rayegan", "configfast", "configms", "configology", "configrayegan", 
    "configt", "configv2rayforfree", "configx2ray", "confing_chanel", "confingam", 
    "confingv2raayng", "confvip", "cook_vpn", "custom_config", "customvpnserver", 
    "daily_configs", "digiv2ray", "do_itforyou", "eliv2ray", "entrynet", "erfwp", 
    "eternal_connect", "ev2rayy", "evay_vpn", "expressvpn_420", "external_net", 
    "fastshovpn", "fergalvpnmod", "filter5050", "filter_breaker", "filterk0sh", 
    "fnet00", "foxnt", "freakconfig", "free_vpn02", "freeconnection_vpn", 
    "freedom_config", "freev2rng", "fsv2ray", "g0dv2ray", "ghalagyann", "ghalagyann2", 
    "ghostray_ng", "golestan_vpn", "green_wpn", "hazaratvpn", "heragabad", "hibyevpnn", 
    "hookvpn_cisco", "hopev2ray", "i10vpn", "icv2ray", "ip_cf", "ipv2ray", 
    "iran_v2ray1", "iraniv2ray", "irlast", "iseqaro", "isvvpn", "itsproxy", 
    "jokerrvpn", "kia_net", "king_v2raay", "lightning6", "ln2ray", "loatvpn", 
    "mahanvpn", "marzazad", "masterserver1", "mdvpnsec", "mehrosaboran", "meli_proxyy", 
    "melov2ray", "mosiv2", "mrsoulb", "mrvpn1403", "msv2ray", "n2vpn", "narcod_ping", 
    "netaccount", "netifyvpn", "netlume", "netmellianti", "nitrovpnv2", 
    "npvv2rayfilter", "nufilter", "outline_vpn", "parsashonam", "pr_vpn", 
    "prime_verse", "prong1", "proxy_tunnel", "pruoxyi", "rezaw_server", "rk_vps", 
    "rnrifci", "saghivpnx", "savteam", "selinc", "server_free2", "shadowproxy66", 
    "shh_proxy", "sobyv2ray", "spdnet", "specialvpn", "specxtech", "spikevpn", 
    "srcvpn", "ssrsub", "svnteam", "tehranargo", "tokavpn", "uciranir", 
    "unlimiteddev", "v2hich", "v2ngfast", "v2ngnet", "v2ray1_ng", "v2ray313", 
    "v2ray_cartel", "v2ray_configs_pool", "v2ray_fark", "v2ray_god", "v2ray_ng", 
    "v2ray_rolly", "v2ray_vmess_free", "v2ray_vpn_ir", "v2rayargon", "v2raybluecrystal", 
    "v2rayfast_7", "v2rayfree1", "v2rayip1", "v2rayn5", "v2rayng3", "v2rayng_1378", 
    "v2rayng_fars", "v2rayng_matsuri", "v2rayngcloud", "v2rayngzendegimamad", 
    "v2rayroz", "v2rayvpn2", "v2ryngfree", "v2safee", "v2wray", "v2xay", "v_2rayngvpn", 
    "vconfing", "venom_servers", "vip_fragment_v2ray", "vipv2rayngnp", "vistav2ray", 
    "viturey", "vmesskhodam", "vmessorg", "vnodepro", "volt_network", "vpn_gaming", 
    "vpn_mikey", "vpn_room", "vpn_zvpn", "vpnandroid2", "vpnjey", "vpnlime", 
    "vpnplusee_free", "vpnserverrr", "vpnshop011", "webshecan", "wedbaztel", 
    "xnxv2ray", "xpnteam", "zdyz2", "zedbaz_vpn", "v2line", "forwardv2ray", 
    "inikotesla", "PrivateVPNs", "VlessConfig", "V2pedia", "v2rayNG_Matsuri", 
    "proxystore11", "DirectVPN", "VmessProtocol", "OutlineVpnOfficial", 
    "networknim", "beiten", "MsV2ray", "foxrayiran", "DailyV2RY", "yaney_01", 
    "EliV2ray", "ServerNett", "v2rayng_fa2", "v2rayng_org", "V2rayNGvpni", 
    "custom_14", "v2rayNG_VPNN", "v2ray_outlineir", "v2_vmess", "FreeVlessVpn", 
    "vmess_vless_v2rayng", "freeland8", "vmessiran", "Outline_Vpn", "vmessq", 
    "WeePeeN", "V2rayNG3", "ShadowsocksM", "shadowsocksshop", "v2rayan", 
    "ShadowSocks_s", "napsternetv_config", "Easy_Free_VPN", "V2Ray_FreedomIran", 
    "V2RAY_VMESS_free", "v2ray_for_free", "V2rayN_Free", "free4allVPN", "vpn_ocean", 
    "FreeV2rays", "DigiV2ray", "v2rayNG_VPN", "freev2rayssr", "v2rayn_server", 
    "Shadowlinkserverr", "iranvpnet", "vmess_iran", "mahsaamoon1", "V2RAY_NEW", 
    "v2RayChannel", "configV2rayNG", "config_v2ray", "vpn_proxy_custom", "vpnmasi", 
    "v2ray_custom", "VPNCUSTOMIZE", "HTTPCustomLand", "ViPVpn_v2ray", "FreeNet1500", 
    "v2ray_ar", "beta_v2ray", "vip_vpn_2022", "FOX_VPN66", "VorTexIRN", "YtTe3la", 
    "V2RayOxygen", "Network_442", "VPN_443", "v2rayng_v", "ultrasurf_12", "iSeqaro", 
    "frev2rayng", "frev2ray", "FreakConfig", "Awlix_ir", "v2rayngvpn", "God_CONFIG", 
    "Configforvpn01","VlessConfig", "MihanV2ray", "Outline_V2rayNG", "VPNINTERNET3", 
    "v2Line", "freev2rayssr", "ConfigsHUB", "VPNCUSTOMIZE", "proxyymeliii", "v2rayconfigsbackup", 
    "v2rayz", "v2ray_vpn_ir", "Mahsa_Proxy", "shadowproxy66", "vpnmasi", "v2raychannel", "UnlimitedV2ray", 
    "MoonVPNir", "proxy_kook", "freedomiranvpn", "H2Proxy", "azadi_proxy", "VPNSHOP3", "v2ray_hub", 
    "v2Rayy_Channel", "PsiphonVPNs", "VPNGOD2024", "FreeVPN2023_M", "WingsVPN"
]

def fetch_channel_content(url):
    """Fetches the HTML content of the Telegram channel page."""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_channel(channel_name):
    """Scrapes a single Telegram channel and returns a list of configs."""
    url = f"https://t.me/s/{channel_name}"
    print(f"Fetching V2Ray configs from {url}...")
    html_content = fetch_channel_content(url)
    
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        configs = parse_v2ray_configs(soup)
        if configs:
            print(f"Found {len(configs)} potential V2Ray configs in {channel_name}.")
            return configs
        else:
            print(f"No V2Ray configs found in {channel_name}.")
    return []

def main():
    all_configs = []
    # Use a ThreadPoolExecutor to scrape channels in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map the scrape_channel function to the list of channel names
        results = executor.map(scrape_channel, TELEGRAM_CHANNEL_NAMES)
        
        # Collect all configs from the results
        for result in results:
            all_configs.extend(result)

    if all_configs:
        # Remove duplicates
        unique_configs = sorted(list(set(all_configs)))
        print(f"\nFound a total of {len(unique_configs)} unique V2Ray configs. Now testing connectivity...")
        
        working_configs = []
        for i, config in enumerate(unique_configs):
            print(f"Testing config {i+1}/{len(unique_configs)}: {config[:50]}...") # Show first 50 chars
            if test_v2ray_config(config):
                working_configs.append(config)
                print(f"Config {i+1} is working.")
            else:
                print(f"Config {i+1} is NOT working.")

        print(f"\nFound {len(working_configs)} working V2Ray configs.")
        save_configs_to_files(working_configs)

        if working_configs:
            subscription_link = generate_subscription_link(working_configs)
            subscription_file_path = os.path.join("v2ray_configs", "subscription.txt")
            with open(subscription_file_path, "w", encoding="utf-8") as f:
                f.write(subscription_link)
            print(f"Generated V2Ray subscription link and saved to {subscription_file_path}")
    else:
        print("\nNo V2Ray configs found across all channels.")

def test_v2ray_config(config_link, timeout=5):
    """
    Tests a single V2Ray config link using Xray and returns True if it's working, False otherwise.
    """
    if not config_link:
        return False

    # Define a temporary file for Xray config
    temp_config_file = None
    xray_process = None
    
    try:
        # Determine protocol and parse the link
        if config_link.startswith("vmess://"):
            # Vmess links are Base64 encoded JSON
            decoded_link = base64.b64decode(config_link[8:]).decode('utf-8')
            config_data = json.loads(decoded_link)
            
            # Construct Xray client config for Vmess
            xray_client_config = {
                "log": {"loglevel": "warning"},
                "inbounds": [
                    {
                        "port": 1080, # Local SOCKS5 proxy port
                        "protocol": "socks",
                        "settings": {"auth": "noauth"}
                    }
                ],
                "outbounds": [
                    {
                        "protocol": "vmess",
                        "settings": {
                            "vnext": [
                                {
                                    "address": config_data["add"],
                                    "port": int(config_data["port"]),
                                    "users": [
                                        {
                                            "id": config_data["id"],
                                            "alterId": int(config_data.get("aid", 0)), # Use .get with default for 'aid'
                                            "level": 0,
                                            "security": "auto"
                                        }
                                    ]
                                }
                            ]
                        },
                        "streamSettings": {
                            "network": config_data.get("net", "tcp"),
                            "security": config_data.get("tls", ""),
                            "tlsSettings": {},
                            "wsSettings": {
                                "path": config_data.get("path", "/"),
                                "headers": {"Host": config_data.get("host", "")}
                            } if config_data.get("net") == "ws" else {},
                            "httpSettings": {
                                "path": config_data.get("path", "/"),
                                "headers": {"Host": config_data.get("host", "")}
                            } if config_data.get("net") == "http" else {}
                        },
                        "tag": "proxy"
                    },
                    {"protocol": "freedom", "tag": "direct"}
                ],
                "routing": {
                    "rules": [
                        {"type": "field", "outboundTag": "proxy", "port": 1080}
                    ]
                }
            }

        elif config_link.startswith("vless://"):
            parsed_url = urllib.parse.urlparse(config_link)
            user_info = parsed_url.netloc.split('@')
            uuid = user_info[0]
            address_port = user_info[1].split(':')
            address = address_port[0]
            port = int(address_port[1])

            query_params = urllib.parse.parse_qs(parsed_url.query)
            # Common Vless stream settings
            network = query_params.get("type", ["tcp"])[0]
            security = query_params.get("security", ["none"])[0]
            flow = query_params.get("flow", [""])[0]
            
            # TLS settings
            tls_settings = {}
            if security == "tls":
                tls_settings["serverName"] = query_params.get("sni", [address])[0]
                tls_settings["allowInsecure"] = query_params.get("allowInsecure", ["0"])[0] == "1"
                tls_settings["alpn"] = query_params.get("alpn", [""])[0].split(',') if query_params.get("alpn") else []
                tls_settings["fingerprint"] = query_params.get("fp", [""])[0]
            elif security == "reality":
                tls_settings["serverName"] = query_params.get("sni", [address])[0]
                tls_settings["fingerprint"] = query_params.get("fp", [""])[0]
                tls_settings["publicKey"] = query_params.get("pbk", [""])[0]
                tls_settings["shortId"] = query_params.get("sid", [""])[0]
                tls_settings["spiderX"] = query_params.get("spx", [""])[0]

            # Stream settings based on network type
            stream_settings = {
                "network": network,
                "security": security,
                "tlsSettings": tls_settings
            }
            if network == "ws":
                stream_settings["wsSettings"] = {
                    "path": query_params.get("path", ["/"])[0],
                    "headers": {"Host": query_params.get("host", [""])[0]}
                }
            elif network == "grpc":
                stream_settings["grpcSettings"] = {
                    "serviceName": query_params.get("serviceName", [""])[0],
                    "multiMode": query_params.get("mode", ["gun"])[0] == "multi"
                }
            
            xray_client_config = {
                "log": {"loglevel": "warning"},
                "inbounds": [
                    {
                        "port": 1080, # Local SOCKS5 proxy port
                        "protocol": "socks",
                        "settings": {"auth": "noauth"}
                    }
                ],
                "outbounds": [
                    {
                        "protocol": "vless",
                        "settings": {
                            "vnext": [
                                {
                                    "address": address,
                                    "port": port,
                                    "users": [
                                        {
                                            "id": uuid,
                                            "encryption": "none",
                                            "flow": flow
                                        }
                                    ]
                                }
                            ]
                        },
                        "streamSettings": stream_settings,
                        "tag": "proxy"
                    },
                    {"protocol": "freedom", "tag": "direct"}
                ],
                "routing": {
                    "rules": [
                        {"type": "field", "outboundTag": "proxy", "port": 1080}
                    ]
                }
            }

        elif config_link.startswith("ss://"):
            parsed_url = urllib.parse.urlparse(config_link)
            
            # The user info part is base64 encoded
            decoded_user_info = base64.b64decode(parsed_url.netloc).decode('utf-8')
            method, password = decoded_user_info.split(':')
            
            address = parsed_url.hostname
            port = parsed_url.port
            
            xray_client_config = {
                "log": {"loglevel": "warning"},
                "inbounds": [
                    {
                        "port": 1080, # Local SOCKS5 proxy port
                        "protocol": "socks",
                        "settings": {"auth": "noauth"}
                    }
                ],
                "outbounds": [
                    {
                        "protocol": "shadowsocks",
                        "settings": {
                            "servers": [
                                {
                                    "address": address,
                                    "port": port,
                                    "method": method,
                                    "password": password
                                }
                            ]
                        },
                        "tag": "proxy"
                    },
                    {"protocol": "freedom", "tag": "direct"}
                ],
                "routing": {
                    "rules": [
                        {"type": "field", "outboundTag": "proxy", "port": 1080}
                    ]
                }
            }
        elif config_link.startswith("trojan://"):
            parsed_url = urllib.parse.urlparse(config_link)
            
            user_info = parsed_url.netloc.split('@')
            password = user_info[0]
            address_port = user_info[1].split(':')
            address = address_port[0]
            port = int(address_port[1])

            query_params = urllib.parse.parse_qs(parsed_url.query)
            # Common Trojan stream settings
            security = query_params.get("security", ["tls"])[0]
            sni = query_params.get("sni", [address])[0]

            xray_client_config = {
                "log": {"loglevel": "warning"},
                "inbounds": [
                    {
                        "port": 1080, # Local SOCKS5 proxy port
                        "protocol": "socks",
                        "settings": {"auth": "noauth"}
                    }
                ],
                "outbounds": [
                    {
                        "protocol": "trojan",
                        "settings": {
                            "servers": [
                                {
                                    "address": address,
                                    "port": port,
                                    "password": password
                                }
                            ]
                        },
                        "streamSettings": {
                            "security": security,
                            "tlsSettings": {"serverName": sni}
                        },
                        "tag": "proxy"
                    },
                    {"protocol": "freedom", "tag": "direct"}
                ],
                "routing": {
                    "rules": [
                        {"type": "field", "outboundTag": "proxy", "port": 1080}
                    ]
                }
            }
        elif config_link.startswith(("hysteria://", "hy2://")):
            parsed_url = urllib.parse.urlparse(config_link)
            
            # Hysteria and Hy2 have different URL structures
            if config_link.startswith("hysteria://"):
                protocol = "hysteria"
                address = parsed_url.hostname
                port = parsed_url.port
                query_params = urllib.parse.parse_qs(parsed_url.query)
                auth = query_params.get("auth", [""])[0]
                up_mbps = int(query_params.get("upmbps", [10])[0])
                down_mbps = int(query_params.get("downmbps", [50])[0])
                
                # Simplified Hysteria config
                xray_client_config = {
                    "log": {"loglevel": "warning"},
                    "inbounds": [{"port": 1080, "protocol": "socks", "settings": {"auth": "noauth"}}],
                    "outbounds": [
                        {
                            "protocol": "hysteria",
                            "settings": {
                                "servers": [
                                    {
                                        "address": address,
                                        "port": port,
                                        "auth": auth,
                                        "up_mbps": up_mbps,
                                        "down_mbps": down_mbps
                                    }
                                ]
                            },
                            "tag": "proxy"
                        },
                        {"protocol": "freedom", "tag": "direct"}
                    ],
                    "routing": {"rules": [{"type": "field", "outboundTag": "proxy", "port": 1080}]}
                }
            
            elif config_link.startswith("hy2://"):
                protocol = "hysteria2"
                user_info = parsed_url.netloc.split('@')
                password = user_info[0]
                address_port = user_info[1].split(':')
                address = address_port[0]
                port = int(address_port[1])
                query_params = urllib.parse.parse_qs(parsed_url.query)
                sni = query_params.get("sni", [address])[0]

                xray_client_config = {
                    "log": {"loglevel": "warning"},
                    "inbounds": [{"port": 1080, "protocol": "socks", "settings": {"auth": "noauth"}}],
                    "outbounds": [
                        {
                            "protocol": "hysteria2",
                            "settings": {
                                "servers": [
                                    {
                                        "address": address,
                                        "port": port,
                                        "password": password
                                    }
                                ]
                            },
                            "streamSettings": {
                                "security": "tls",
                                "tlsSettings": {"serverName": sni}
                            },
                            "tag": "proxy"
                        },
                        {"protocol": "freedom", "tag": "direct"}
                    ],
                    "routing": {"rules": [{"type": "field", "outboundTag": "proxy", "port": 1080}]}
                }
        else:
            print(f"Unsupported protocol for testing: {config_link}")
            return False

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(xray_client_config, f)
            temp_config_file = f.name
        
        # Start Xray process
        # We need to ensure 'xray' executable is in PATH
        xray_command = ["xray", "-c", temp_config_file]
        try:
            xray_process = subprocess.Popen(xray_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            print(f"Error: 'xray' executable not found. Please ensure Xray is installed and in your system's PATH. "
                  f"For local execution, download from https://github.com/XTLS/Xray-core/releases and add to PATH.")
            return False
        
        time.sleep(1) # Give Xray some time to start

        # Test connectivity through the proxy
        proxies = {
            "http": "socks5://127.0.0.1:1080",
            "https": "socks5://127.0.0.1:1080"
        }
        test_url = "http://www.google.com/generate_204" # A reliable test URL that returns 204 No Content

        try:
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            return response.status_code == 204
        except requests.exceptions.RequestException as e:
            print(f"Connectivity test failed for {config_link}: {e}")
            return False

    except Exception as e:
        print(f"An error occurred during config testing for {config_link}: {e}")
        return False
    finally:
        # Clean up
        if xray_process:
            xray_process.terminate()
            xray_process.wait(timeout=1) # Give it a moment to terminate
            if xray_process.poll() is None: # If still running
                xray_process.kill()
        if temp_config_file and os.path.exists(temp_config_file):
            os.remove(temp_config_file)

def parse_v2ray_configs(soup):
    """Parses the BeautifulSoup object to find V2Ray config strings."""
    configs = []
    protocols = ["vmess", "vless", "ss", "trojan", "hysteria", "hysteria2", "hy2"]
    protocol_headers_regex = "|".join([re.escape(p + "://") for p in protocols])

    # Find all message text elements
    message_texts = soup.find_all("div", class_="tgme_widget_message_text")
    for message in message_texts:
        # Find all <code> blocks within a message
        code_blocks = message.find_all("code")
        for block in code_blocks:
            config_text = block.get_text().strip()
            
            # Find all starting positions of the configs
            start_indices = [m.start() for m in re.finditer(protocol_headers_regex, config_text)]
            
            for i in range(len(start_indices)):
                start = start_indices[i]
                end = start_indices[i+1] if i+1 < len(start_indices) else len(config_text)
                
                # Extract the config string
                config_str = config_text[start:end].strip()
                
                # Basic validation: ensure it actually starts with a known protocol
                if any(config_str.startswith(p + "://") for p in protocols):
                    configs.append(config_str)
    return configs

def save_configs_to_files(configs):
    """Saves the extracted configs into single files sorted by protocol."""
    # Define output directory
    output_dir = "v2ray_configs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Group configs by protocol
    grouped_configs = {"vmess": [], "vless": [], "ss": [], "hysteria": [], "trojan": []} # Remove hysteria2 as a separate key
    for config in configs:
        match = re.match(r"(\w+):\/\/", config)
        if match:
            protocol = match.group(1)
            # Unify hysteria, hysteria2, and hy2 under 'hysteria'
            if protocol in ["hysteria2", "hy2"]:
                protocol = "hysteria"
            
            if protocol in grouped_configs:
                grouped_configs[protocol].append(config)

    # Process and save each protocol's configs
    for protocol, config_list in grouped_configs.items():
        if not config_list:
            continue

        # Join all configs with a newline
        combined_configs = "\n".join(config_list)
        
        # Save to a single file
        file_path = os.path.join(output_dir, f"{protocol}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(combined_configs)
        print(f"Saved {len(config_list)} {protocol} configs to {file_path}")

def generate_subscription_link(configs):
    """Generates a Base64 encoded V2Ray subscription link from a list of configs."""
    combined_configs = "\n".join(configs)
    encoded_bytes = base64.b64encode(combined_configs.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

if __name__ == "__main__":
    main()