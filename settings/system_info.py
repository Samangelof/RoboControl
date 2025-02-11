import psutil
import platform
from datetime import datetime
import cpuinfo
import socket
import uuid
import re
from settings.logger import setup_logger


logger = setup_logger(__name__)



def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def system_information():
    logger.debug(f'{"="*40} "System Information" {"="*40}')
    uname = platform.uname()
    logger.debug(f"System: {uname.system}")
    logger.debug(f"Node Name: {uname.node}")
    logger.debug(f"Release: {uname.release}")
    logger.debug(f"Version: {uname.version}")
    logger.debug(f"Machine: {uname.machine}")
    logger.debug(f"Processor: {uname.processor}")
    logger.debug(f"Processor: {cpuinfo.get_cpu_info()['brand_raw']}")
    logger.debug(f"Ip-Address: {socket.gethostbyname(socket.gethostname())}")
    logger.debug(f"Mac-Address: {':'.join(re.findall('..', '%012x' % uuid.getnode()))}")


    # # Boot Time
    # logger.debug("="*40, "Boot Time", "="*40)
    # boot_time_timestamp = psutil.boot_time()
    # bt = datetime.fromtimestamp(boot_time_timestamp)
    # logger.debug(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")


    # logger.debug CPU information
    logger.debug(f'{"="*40} "CPU Info" {"="*40}')

    # number of cores
    logger.debug(f"Physical cores:, {psutil.cpu_count(logical=False)}")
    logger.debug(f"Total cores: {psutil.cpu_count(logical=True)}")
    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    logger.debug(f"Max Frequency: {cpufreq.max:.2f}Mhz")
    logger.debug(f"Min Frequency: {cpufreq.min:.2f}Mhz")
    logger.debug(f"Current Frequency: {cpufreq.current:.2f}Mhz")
    # CPU usage
    logger.debug("CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        logger.debug(f"Core {i}: {percentage}%")
    logger.debug(f"Total CPU Usage: {psutil.cpu_percent()}%")


    # Memory Information
    logger.debug(f'{"="*40} "Memory Information" {"="*40}')
    # get the memory details
    svmem = psutil.virtual_memory()
    logger.debug(f"Total: {get_size(svmem.total)}")
    logger.debug(f"Available: {get_size(svmem.available)}")
    logger.debug(f"Used: {get_size(svmem.used)}")
    logger.debug(f"Percentage: {svmem.percent}%")



    # logger.debug("="*20, "SWAP", "="*20)
    # # get the swap memory details (if exists)
    # swap = psutil.swap_memory()
    # logger.debug(f"Total: {get_size(swap.total)}")
    # logger.debug(f"Free: {get_size(swap.free)}")
    # logger.debug(f"Used: {get_size(swap.used)}")
    # logger.debug(f"Percentage: {swap.percent}%")



    # Disk Information
    logger.debug(f'{"="*40} "Disk Information" {"="*40}')
    logger.debug("Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        logger.debug(f"=== Device: {partition.device} ===")
        logger.debug(f"  Mountpoint: {partition.mountpoint}")
        logger.debug(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        logger.debug(f"  Total Size: {get_size(partition_usage.total)}")
        logger.debug(f"  Used: {get_size(partition_usage.used)}")
        logger.debug(f"  Free: {get_size(partition_usage.free)}")
        logger.debug(f"  Percentage: {partition_usage.percent}%")
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    logger.debug(f"Total read: {get_size(disk_io.read_bytes)}")
    logger.debug(f"Total write: {get_size(disk_io.write_bytes)}")
    logger.debug("="*100)

    # ## Network information
    # logger.debug("="*40, "Network Information", "="*40)
    # ## get all network interfaces (virtual and physical)
    # if_addrs = psutil.net_if_addrs()
    # for interface_name, interface_addresses in if_addrs.items():
    #     for address in interface_addresses:
    #         logger.debug(f"=== Interface: {interface_name} ===")
    #         if str(address.family) == 'AddressFamily.AF_INET':
    #             logger.debug(f"  IP Address: {address.address}")
    #             logger.debug(f"  Netmask: {address.netmask}")
    #             logger.debug(f"  Broadcast IP: {address.broadcast}")
    #         elif str(address.family) == 'AddressFamily.AF_PACKET':
    #             logger.debug(f"  MAC Address: {address.address}")
    #             logger.debug(f"  Netmask: {address.netmask}")
    #             logger.debug(f"  Broadcast MAC: {address.broadcast}")
    # ##get IO statistics since boot
    # net_io = psutil.net_io_counters()
    # logger.debug(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    # logger.debug(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")


# if __name__ == "__main__":
#     system_information()