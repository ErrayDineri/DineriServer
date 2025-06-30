# dashboard/services/system_monitor.py
import psutil
import platform
import time
import datetime
from typing import Dict, Any, Optional
import json


class SystemMonitor:
    """Cross-platform system monitoring service for Windows and Linux."""
    
    def __init__(self):
        self.system = platform.system()
        self.start_time = time.time()
        self._last_network_stats = None
        self._last_network_time = None
    
    def get_cpu_usage(self) -> Dict[str, Any]:
        """Get CPU usage information."""
        try:
            # Get CPU usage percentage (averaged over 1 second)
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # Get CPU frequency
            cpu_freq = psutil.cpu_freq()
            current_freq = cpu_freq.current if cpu_freq else 0
            max_freq = cpu_freq.max if cpu_freq else 0
            
            # Get load average (Linux/Unix only)
            load_avg = None
            if self.system != "Windows":
                try:
                    load_avg = psutil.getloadavg()
                except AttributeError:
                    pass
            
            return {
                "usage_percent": round(cpu_percent, 1),
                "cores_physical": cpu_count,
                "cores_logical": cpu_count_logical,
                "frequency_current": round(current_freq, 1) if current_freq else None,
                "frequency_max": round(max_freq, 1) if max_freq else None,
                "load_average": load_avg,
                "status": self._get_cpu_status(cpu_percent)
            }
        except Exception as e:
            return {
                "usage_percent": 0,
                "error": str(e),
                "status": "error"
            }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information."""
        try:
            # Virtual memory stats
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total_gb": round(memory.total / (1024**3), 1),
                "available_gb": round(memory.available / (1024**3), 1),
                "used_gb": round(memory.used / (1024**3), 1),
                "usage_percent": round(memory.percent, 1),
                "swap_total_gb": round(swap.total / (1024**3), 1),
                "swap_used_gb": round(swap.used / (1024**3), 1),
                "swap_percent": round(swap.percent, 1),
                "status": self._get_memory_status(memory.percent)
            }
        except Exception as e:
            return {
                "total_gb": 0,
                "available_gb": 0,
                "used_gb": 0,
                "usage_percent": 0,
                "error": str(e),
                "status": "error"
            }
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information."""
        try:
            disks = []
            total_size = 0
            total_used = 0
            
            # Get all disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    # Skip special filesystems on Linux
                    if self.system == "Linux" and partition.fstype in ['tmpfs', 'devtmpfs', 'proc', 'sysfs']:
                        continue
                    
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    disk_info = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 1),
                        "used_gb": round(usage.used / (1024**3), 1),
                        "free_gb": round(usage.free / (1024**3), 1),
                        "usage_percent": round((usage.used / usage.total) * 100, 1)
                    }
                    
                    disks.append(disk_info)
                    total_size += usage.total
                    total_used += usage.used
                    
                except PermissionError:
                    # Skip inaccessible drives
                    continue
            
            # Calculate overall disk usage
            overall_percent = round((total_used / total_size) * 100, 1) if total_size > 0 else 0
            
            return {
                "disks": disks,
                "total_gb": round(total_size / (1024**3), 1),
                "used_gb": round(total_used / (1024**3), 1),
                "free_gb": round((total_size - total_used) / (1024**3), 1),
                "usage_percent": overall_percent,
                "status": self._get_disk_status(overall_percent)
            }
        except Exception as e:
            return {
                "disks": [],
                "total_gb": 0,
                "used_gb": 0,
                "free_gb": 0,
                "usage_percent": 0,
                "error": str(e),
                "status": "error"
            }
    
    def get_network_usage(self) -> Dict[str, Any]:
        """Get network usage information."""
        try:
            # Get network I/O statistics
            network_io = psutil.net_io_counters()
            current_time = time.time()
            
            # Calculate bandwidth if we have previous measurements
            bandwidth_mbps = 0
            if self._last_network_stats and self._last_network_time:
                time_diff = current_time - self._last_network_time
                bytes_diff = (network_io.bytes_sent + network_io.bytes_recv) - \
                           (self._last_network_stats.bytes_sent + self._last_network_stats.bytes_recv)
                
                if time_diff > 0:
                    # Convert to Mbps
                    bandwidth_mbps = round((bytes_diff * 8) / (time_diff * 1000000), 2)
            
            # Store current stats for next calculation
            self._last_network_stats = network_io
            self._last_network_time = current_time
            
            # Get network interfaces
            interfaces = []
            net_if_stats = psutil.net_if_stats()
            net_if_addrs = psutil.net_if_addrs()
            
            for interface_name, stats in net_if_stats.items():
                if stats.isup and interface_name in net_if_addrs:
                    # Get IP addresses for this interface
                    addresses = []
                    for addr in net_if_addrs[interface_name]:
                        if addr.family.name in ['AF_INET', 'AF_INET6']:
                            addresses.append({
                                "family": addr.family.name,
                                "address": addr.address
                            })
                    
                    interfaces.append({
                        "name": interface_name,
                        "is_up": stats.isup,
                        "speed": stats.speed,
                        "addresses": addresses
                    })
            
            return {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv,
                "bandwidth_mbps": bandwidth_mbps,
                "interfaces": interfaces,
                "total_gb_sent": round(network_io.bytes_sent / (1024**3), 2),
                "total_gb_recv": round(network_io.bytes_recv / (1024**3), 2),
                "status": self._get_network_status(bandwidth_mbps)
            }
        except Exception as e:
            return {
                "bytes_sent": 0,
                "bytes_recv": 0,
                "bandwidth_mbps": 0,
                "interfaces": [],
                "error": str(e),
                "status": "error"
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information."""
        try:
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            
            # Format uptime
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            uptime_str = ""
            if days > 0:
                uptime_str += f"{days}d "
            uptime_str += f"{hours}h {minutes}m"
            
            return {
                "platform": platform.platform(),
                "system": platform.system(),
                "processor": platform.processor(),
                "architecture": platform.architecture()[0],
                "hostname": platform.node(),
                "python_version": platform.python_version(),
                "boot_time": boot_time.isoformat(),
                "uptime": uptime_str,
                "uptime_seconds": int(uptime.total_seconds())
            }
        except Exception as e:
            return {
                "platform": "Unknown",
                "error": str(e)
            }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get all system statistics."""
        return {
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "network": self.get_network_usage(),
            "system": self.get_system_info(),
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _get_cpu_status(self, usage_percent: float) -> str:
        """Determine CPU status based on usage."""
        if usage_percent < 30:
            return "good"
        elif usage_percent < 70:
            return "warning"
        else:
            return "critical"
    
    def _get_memory_status(self, usage_percent: float) -> str:
        """Determine memory status based on usage."""
        if usage_percent < 60:
            return "good"
        elif usage_percent < 85:
            return "warning"
        else:
            return "critical"
    
    def _get_disk_status(self, usage_percent: float) -> str:
        """Determine disk status based on usage."""
        if usage_percent < 80:
            return "good"
        elif usage_percent < 95:
            return "warning"
        else:
            return "critical"
    
    def _get_network_status(self, bandwidth_mbps: float) -> str:
        """Determine network status based on activity."""
        if bandwidth_mbps < 1:
            return "idle"
        elif bandwidth_mbps < 10:
            return "active"
        else:
            return "busy"


# Global instance
system_monitor = SystemMonitor()
