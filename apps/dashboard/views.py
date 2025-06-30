from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .services.system_monitor import system_monitor
import json


class HomeView(View):
    def get(self, request):
        # Get initial system stats for the dashboard
        try:
            stats = system_monitor.get_all_stats()
        except Exception as e:
            # Fallback to mock data if monitoring fails
            stats = {
                "cpu": {"usage_percent": 0, "status": "error"},
                "memory": {"usage_percent": 0, "total_gb": 0, "used_gb": 0, "status": "error"},
                "disk": {"usage_percent": 0, "total_gb": 0, "used_gb": 0, "status": "error"},
                "network": {"bandwidth_mbps": 0, "status": "error"},
                "system": {"uptime": "Unknown", "error": str(e)}
            }
        
        return render(request, 'dashboard/home.html', {'system_stats': stats})


@method_decorator(login_required, name='dispatch')
class SystemStatsAPIView(View):
    def get(self, request):
        """API endpoint to get real-time system statistics."""
        try:
            stats = system_monitor.get_all_stats()
            return JsonResponse(stats)
        except Exception as e:
            return JsonResponse({
                "error": str(e),
                "cpu": {"usage_percent": 0, "status": "error"},
                "memory": {"usage_percent": 0, "total_gb": 0, "used_gb": 0, "status": "error"},
                "disk": {"usage_percent": 0, "total_gb": 0, "used_gb": 0, "status": "error"},
                "network": {"bandwidth_mbps": 0, "status": "error"},
                "system": {"uptime": "Unknown"}
            }, status=500)