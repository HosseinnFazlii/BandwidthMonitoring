# bandwidth/tasks.py
import requests
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Server

def calculate_bandwidth_for_server(server_id):
    server = get_object_or_404(Server, id=server_id)
    
    hostname = server.panel_ipaddress
    port = server.panel_port
    api_key = server.api_key
    api_password = server.api_password
    vps_id = server.vps_id

    telegram_bot_token = server.telegramAPItoken
    telegram_chat_id1 = server.chat_ID1
    telegram_chat_id2 = server.chat_ID2

    url = f"http://{hostname}:{port}/index.php"
    params = {
        'act': 'vpsmanage',
        'svs': vps_id,
        'api': 'json',
        'apikey': api_key,
        'apipass': api_password
    }

    try:
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()
        
        bandwidth_info = data['info']['bandwidth']
        limit_bandwidth = bandwidth_info['limit']
        used_bandwidth = bandwidth_info['used']
        free_bandwidth = bandwidth_info['free']
        
        server.limit_bandwidth_gb = limit_bandwidth / 1024
        server.used_bandwidth_gb = used_bandwidth / 1024
        server.free_bandwidth_gb = free_bandwidth / 1024
        server.save()

        if used_bandwidth >= 0.1 * limit_bandwidth:
            message = (f"Alert! Used bandwidth is over 80% "
                       f" you vps host name is  ({server.hostname}).")
            
            telegram_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
            telegram_params1 = {'chat_id': telegram_chat_id1, 'text': message}
            telegram_params2 = {'chat_id': telegram_chat_id2, 'text': message}
            
            requests.get(telegram_url, params=telegram_params1)
            requests.get(telegram_url, params=telegram_params2)

    except requests.RequestException as e:
        print("Error:", e)
    except ValueError as e:
        print("Error parsing JSON response:", e)

# bandwidth/tasks.py
def calculate_bandwidth_for_all_servers():
    servers = Server.objects.all()
    for server in servers:
        calculate_bandwidth_for_server(server.id)
