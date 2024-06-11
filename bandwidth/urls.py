from django.urls import path
from .views import server_list_view, bandwidth_usage_view

urlpatterns = [
    path('', server_list_view, name='server_list'),
    path('server/<int:server_id>/bandwidth/', bandwidth_usage_view, name='bandwidth_usage'),
]
