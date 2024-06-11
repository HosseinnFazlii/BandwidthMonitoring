from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Server

class ServerAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'ip_address', 'api_key', 'api_password','panel_ipaddress','vps_id','panel_port','telegramAPItoken','chat_ID1','chat_ID2')
    search_fields = ('hostname', 'ip_address')

admin.site.register(Server, ServerAdmin)
