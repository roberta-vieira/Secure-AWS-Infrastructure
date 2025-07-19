#!/usr/bin/env python3

import subprocess      # Runs systems commands like installing packages or executing nmap
import socket          # Works with IP addresses and network related functions
import sys             # Provides access to system-level details, such as current Python interpreter (e.g. for installing packages with the correct version)
import os              # Allows interaction with the OS (e.g. environment variables)

# --- STEP 1: Ensure dependencies are installed ---
def install_requirements():
    try:
        import netifaces
    except ImportError:
        print("Installing required Python package: netifaces")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "netifaces"])
    
    if subprocess.call(["which", "nmap"], stdout=subprocess.DEVNULL) != 0:
        print("Installing nmap...")
        try:
            subprocess.check_call(["sudo", "yum", "install", "-y", "nmap"])
        except subprocess.CalledProcessError:
            subprocess.check_call(["sudo", "dnf", "install", "-y", "nmap"])

# --- STEP 2: Get private IP ---
def get_private_ip():
    import netifaces                # Used to access netwrok interface details (e.g. IP and MAC addresses)
    interfaces = netifaces.interfaces()
    for iface in interfaces:
        try:
            iface_ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
            if iface_ip.startswith(("10.", "192.168.", "172.")):
                return iface_ip
        except:
            continue
    raise RuntimeError("Could not detect private IP address.")

# --- STEP 3: Build subnets to scan ---
def get_subnets_from_ip(ip):
    if ip.startswith("10."):
        return ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]
    elif ip.startswith("192.168."):
        return ["192.168.0.0/24", "192.168.1.0/24", "192.168.2.0/24"]
    elif ip.startswith("172."):
        return ["172.16.0.0/24", "172.16.1.0/24", "172.16.2.0/24"]
    else:
        return [ip + "/24"]

# --- STEP 4: Ping sweep to find active IPs ---
def find_live_hosts(subnet):
    print(f"\n🔍 Scanning subnet {subnet} for live hosts...")
    result = subprocess.run(["nmap", "-sn", subnet], capture_output=True, text=True)
    live_hosts = []
    for line in result.stdout.splitlines():
        if line.startswith("Nmap scan report for"):
            ip = line.split()[-1].strip("()")
            live_hosts.append(ip)
            print(f"🟢 Host is up: {ip}")
    return live_hosts

# --- STEP 5: Port scan each live host ---
def scan_open_ports(host_ip):
    print(f"\n🚨 Scanning {host_ip} for open ports...")
    result = subprocess.run(["sudo", "nmap", "-sS", "-T4", "-F", host_ip], capture_output=True, text=True)
    print(result.stdout)

# --- MAIN ---
if __name__ == "__main__":
    install_requirements()
    ip = get_private_ip()
    subnets = get_subnets_from_ip(ip)
    print(f"Detected IP: {ip} → Scanning subnets: {subnets}")

    all_live_hosts = []
    for subnet in subnets:
        live_hosts = find_live_hosts(subnet)
        all_live_hosts.extend(live_hosts)

    if not all_live_hosts:
        print("\n❌ No live hosts found.")
    else:
        print(f"\n✅ Total live hosts found: {len(all_live_hosts)}")
        for host in all_live_hosts:
            scan_open_ports(host)
