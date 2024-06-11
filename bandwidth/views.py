import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Server
from datetime import datetime
import json

def bandwidth_usage_view(request, server_id):
    server = get_object_or_404(Server, id=server_id)
    
    # Get the current month in the format YYYYMM
         # Replace these values with your actual server details
    hostname = server.panel_ipaddress
    port = server.panel_port
    api_key = server.api_key
    api_password = server.api_password
    vps_id = server.vps_id  # Replace with the ID of your VPS

# Telegram bot details
    telegram_bot_token = server.telegramAPItoken
    telegram_chat_id1 = server.chat_ID1
    telegram_chat_id2=server.chat_ID2

# Construct the URL
    url = f"http://{hostname}:{port}/index.php"

# Construct the query parameters
    params = {
    'act': 'vpsmanage',
    'svs': vps_id,
    'api': 'json',
    'apikey': api_key,
    'apipass': api_password
    }

    try:
    # Make the request
        response = requests.get(url, params=params, verify=False)  # Use verify=False to ignore SSL certificate verification
        response.raise_for_status()  # Raise an HTTPError on bad response
    
    # Print the response content
        print("Response content:", response.content)
    
    # Parse JSON response if needed
        data = response.json()
        print("Parsed JSON data:", data)

    # Extracting bandwidth information
        bandwidth_info = data['info']['bandwidth']
    
    # Extracting specific bandwidth data
        limit_bandwidth = bandwidth_info['limit']
        used_bandwidth = bandwidth_info['used']
        free_bandwidth = bandwidth_info['free']
    
    # Convert MB to GB
        server.limit_bandwidth_gb = limit_bandwidth / 1024
        server.used_bandwidth_gb = used_bandwidth / 1024
        server.free_bandwidth_gb = free_bandwidth / 1024
        server.save()
    

    # Check if used bandwidth exceeds 80% of the limit
        if used_bandwidth >= 0.01 * limit_bandwidth:
        # Send a notification to Telegram
            message = f"Alert! Used bandwidth is at {server.used_bandwidth_gb:.2f} GB which is over 80% of the limit ({server.limit_bandwidth_gb:.2f} GB), you vps id is ({server.hostname})."
        
            telegram_url1 = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
            telegram_url2 = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
            telegram_params1 = {
                'chat_id': telegram_chat_id1,
                'text': message
            }
            telegram_params2 = {
                'chat_id': telegram_chat_id2,
                'text': message
            }
        
            telegram_response1 = requests.get(telegram_url1, params=telegram_params1)
            telegram_response2 = requests.get(telegram_url2, params=telegram_params2)
            response1=telegram_response1.raise_for_status()
            response2=telegram_response2.raise_for_status()  # Raise an HTTPError on bad response
            

    except requests.RequestException as e:
        print("Error:", e)
    except ValueError as e:
        print("Error parsing JSON response:", e)

    bandwidth_usage = server.used_bandwidth_gb
    in_usage = server.limit_bandwidth_gb
    out_usage = server.free_bandwidth_gb
    
    # Calculate percentage values
    total_bandwidth = in_usage
    used_percent = (bandwidth_usage / total_bandwidth) * 100
    remaining_percent = 100 - used_percent
    
    context = {
        'server': server,
        'bandwidth_usage': bandwidth_usage,
        'in_usage': in_usage,
        'out_usage': out_usage,
        'used_percent': used_percent,
        'remaining_percent': remaining_percent
    }
    return render(request, 'bandwidth/bandwidth_usage.html', context)

def server_list_view(request):
    servers = Server.objects.all()
    return render(request, 'templates/bandwidth/server_list.html', {'servers': servers})

