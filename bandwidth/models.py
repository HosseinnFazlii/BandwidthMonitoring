from django.db import models

class Server(models.Model):
    hostname = models.CharField(max_length=255, unique=True, help_text="Hostname of the server")
    ip_address = models.GenericIPAddressField(protocol='both', unpack_ipv4=False, help_text="IP address of the server")
    api_key=models.CharField(max_length=255)
    api_password=models.CharField(max_length=255)
    panel_ipaddress=models.CharField(max_length=255)
    vps_id=models.IntegerField(default=0)
    panel_port=models.IntegerField(default=0)
    telegramAPItoken=models.CharField(max_length=255)
    chat_ID1=models.IntegerField(default=0)
    chat_ID2=models.IntegerField(default=0)
    used_bandwidth_gb=models.CharField(max_length=255)
    limit_bandwidth_gb=models.CharField(max_length=255)
    free_bandwidth_gb=models.CharField(max_length=255)
    scheme = models.CharField(max_length=5, choices=[('http', 'http'), ('https', 'https')], default='https')

   

