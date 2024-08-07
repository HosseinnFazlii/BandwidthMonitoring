# bandwidth/tasks.py

from celery import shared_task
import requests
import logging
from django.shortcuts import get_object_or_404
from .models import Server

logger = logging.getLogger('bandwidth')

@shared_task
def calculate_bandwidth_for_server(server_id):
    logger.debug(f"Starting bandwidth calculation for server {server_id}")
    server = get_object_or_404(Server, id=server_id)
    scheme = server.scheme   
    hostname = server.panel_ipaddress
    port = server.panel_port
    api_key = server.api_key
    api_password = server.api_password
    vps_id = server.vps_id

    telegram_bot_token = server.telegramAPItoken
    telegram_chat_id1 = server.chat_ID1
    telegram_chat_id2 = server.chat_ID2
    
    url = f"{scheme}://{hostname}:{port}/index.php"
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


        logger.debug(f"Bandwidth calculation completed for server {server_id}")

    except requests.RequestException as e:
        logger.error(f"Error during bandwidth calculation for server {server_id}: {e}")
    except ValueError as e:
        logger.error(f"Error parsing JSON response for server {server_id}: {e}")

@shared_task
def calculate_bandwidth_for_all_servers():
    logger.debug("Starting bandwidth calculation for all servers")
    servers = Server.objects.all()
    for server in servers:
        calculate_bandwidth_for_server.delay(server.id)
    logger.debug("Bandwidth calculation completed for all servers")
