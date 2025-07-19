# Internal Network Reconnaissance Script

This Python script simulates a common **Discovery** tactic from the MITRE ATT&CK framework. It is intended to be executed from a compromised EC2 instance to mimic a post-exploitation scenario where an attacker scans the internal network to identify live hosts and exposed ports.

> ⚠️ This script is designed for **Linux-based environments** only. It will not function properly on Windows systems.

## Objective

- Simulate network reconnaissance from within the AWS environment.
- Detect live hosts using a ping sweep (`nmap -sn`) across private subnets.
- Scan for open ports on each host using a stealth TCP SYN scan (`nmap -sS`).
- Trigger GuardDuty findings to validate visibility and detection.

## How It Works

1. **Dependency Check:**  
   - Automatically installs required Python packages (`netifaces`) and `nmap` (via `yum` or `dnf`).
2. **Private IP Detection:**  
   - Identifies the EC2 instance's private IP to infer the VPC range.
3. **Subnet Selection:**  
   - Scans only the **first three /24 subnets** (e.g., `10.0.0.0/24`, `10.0.1.0/24`, `10.0.2.0/24`) to reduce scan time during testing.  
   - For more comprehensive reconnaissance, consider scanning the full **VPC CIDR range** (e.g., `/16`).
4. **Host Discovery:**  
   - Performs a ping sweep to identify reachable hosts.
5. **Port Scanning:**  
   - Performs a fast SYN scan (`-F -T4`) to enumerate open ports on detected hosts.

> ⚠️ **Note:** Hosts that are hardened and do not respond to ping (ICMP) may not appear in this scan. This is a preliminary discovery method.

## Usage

```bash
chmod +x active_recon.py
./active_recon.py
