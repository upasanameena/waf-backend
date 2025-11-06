#!/usr/bin/env python3
"""
Network Layer Firewall - Dual-Layer Firewall System
Intercepts packets at network layer and applies ML-based blocking
"""

import netfilterqueue
import socket
import struct
import threading
import time
import csv
import os
from scapy.all import IP, TCP, UDP, ICMP
import numpy as np
import pickle

# Network firewall model (separate from WAF model)
NETWORK_MODEL_PATH = 'network_firewall_model.pkl'
NETWORK_BLOCKED_CSV = 'network_blocked.csv'
NETWORK_ALLOWED_CSV = 'network_allowed.csv'

# Load network model if exists, otherwise create dummy
try:
    with open(NETWORK_MODEL_PATH, 'rb') as f:
        network_model = pickle.load(f)
    print(f"[NETWORK FIREWALL] Loaded model from {NETWORK_MODEL_PATH}")
except FileNotFoundError:
    print(f"[NETWORK FIREWALL] No model found, using rule-based detection only")
    network_model = None

# Suspicious IP patterns (for demonstration)
SUSPICIOUS_IPS = set()
BLOCKED_IPS = set()

# Rate limiting
connection_counts = {}
last_reset = time.time()

def extract_network_features(packet):
    """Extract features from network packet"""
    try:
        # Get raw packet data
        raw_packet = packet.get_payload()
        ip_layer = IP(raw_packet)
        
        # Basic features
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
        protocol = ip_layer.proto  # 1=ICMP, 6=TCP, 17=UDP
        
        # Packet size
        packet_size = len(raw_packet)
        
        # Port information
        src_port = 0
        dst_port = 0
        
        if ip_layer.haslayer(TCP):
            src_port = ip_layer[TCP].sport
            dst_port = ip_layer[TCP].dport
            flags = ip_layer[TCP].flags
        elif ip_layer.haslayer(UDP):
            src_port = ip_layer[UDP].sport
            dst_port = ip_layer[UDP].dport
            flags = 0
        else:
            flags = 0
        
        # IP-based features
        src_ip_numeric = ip_to_int(src_ip)
        dst_ip_numeric = ip_to_int(dst_ip)
        
        # Feature vector: [src_ip_hash, dst_ip_hash, protocol, src_port, dst_port, packet_size, flags]
        # Normalize for ML model
        features = [
            src_ip_numeric % 10000,  # Hash to manageable range
            dst_ip_numeric % 10000,
            protocol,
            src_port,
            dst_port,
            packet_size,
            flags
        ]
        
        return {
            'features': features,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_port': src_port,
            'dst_port': dst_port,
            'protocol': protocol,
            'packet_size': packet_size,
            'flags': flags
        }
    except Exception as e:
        print(f"[NETWORK FIREWALL] Error extracting features: {e}")
        return None

def ip_to_int(ip):
    """Convert IP address to integer"""
    try:
        return struct.unpack("!I", socket.inet_aton(ip))[0]
    except:
        return 0

def is_suspicious_network(features_dict):
    """Check if network packet is suspicious using ML + rules"""
    if not features_dict:
        return False, "Invalid packet"
    
    src_ip = features_dict['src_ip']
    dst_port = features_dict['dst_port']
    protocol = features_dict['protocol']
    packet_size = features_dict['packet_size']
    
    # Rule 1: Blocked IP list
    if src_ip in BLOCKED_IPS:
        return True, "Blocked IP"
    
    # Rule 2: Suspicious ports (common attack ports)
    suspicious_ports = [22, 23, 3389, 1433, 3306, 5432, 27017]  # SSH, Telnet, RDP, DB ports
    if dst_port in suspicious_ports and protocol == 6:  # TCP
        return True, f"Suspicious port: {dst_port}"
    
    # Rule 3: Large packets (potential DDoS)
    if packet_size > 1500:
        return True, "Oversized packet"
    
    # Rule 4: ML model prediction (if available)
    if network_model:
        try:
            features = np.array(features_dict['features']).reshape(1, -1)
            prediction = network_model.predict(features)[0]
            if hasattr(network_model, 'predict_proba'):
                proba = network_model.predict_proba(features)[0]
                malicious_prob = proba[1] if len(proba) > 1 else proba[0]
                if malicious_prob > 0.7:
                    return True, f"ML prediction: {malicious_prob:.2%}"
            elif prediction == 1:
                return True, "ML prediction: malicious"
        except Exception as e:
            pass  # Fall back to rules
    
    # Rule 5: Rate limiting (connection flooding)
    current_time = time.time()
    if current_time - last_reset > 60:  # Reset every minute
        connection_counts.clear()
    
    key = f"{src_ip}:{dst_port}"
    connection_counts[key] = connection_counts.get(key, 0) + 1
    
    if connection_counts[key] > 100:  # More than 100 connections/min
        BLOCKED_IPS.add(src_ip)
        return True, "Rate limit exceeded"
    
    return False, "Allowed"

def log_network_decision(decision, features_dict, reason):
    """Log network firewall decision to CSV"""
    if not features_dict:
        return
    
    csv_file = NETWORK_BLOCKED_CSV if decision else NETWORK_ALLOWED_CSV
    
    # Check if file exists, create with header if not
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 
                           'protocol', 'packet_size', 'reason'])
        
        writer.writerow([
            time.time(),
            features_dict['src_ip'],
            features_dict['dst_ip'],
            features_dict['src_port'],
            features_dict['dst_port'],
            features_dict['protocol'],
            features_dict['packet_size'],
            reason
        ])

def process_packet(packet):
    """Process each intercepted packet"""
    try:
        features_dict = extract_network_features(packet)
        
        if not features_dict:
            packet.accept()
            return
        
        is_malicious, reason = is_suspicious_network(features_dict)
        
        # Log decision
        log_network_decision(is_malicious, features_dict, reason)
        
        if is_malicious:
            print(f"[NETWORK BLOCKED] {features_dict['src_ip']}:{features_dict['src_port']} -> "
                  f"{features_dict['dst_ip']}:{features_dict['dst_port']} | Reason: {reason}")
            packet.drop()  # Block the packet
        else:
            packet.accept()  # Allow the packet
            
    except Exception as e:
        print(f"[NETWORK FIREWALL] Error processing packet: {e}")
        packet.accept()  # Default to allow on error

def setup_iptables_queue():
    """Setup iptables rules to forward packets to NFQUEUE"""
    import subprocess
    
    # Flush existing rules
    subprocess.run(['sudo', 'iptables', '-F'], check=False)
    subprocess.run(['sudo', 'iptables', '-X'], check=False)
    
    # Forward all INPUT traffic to NFQUEUE
    subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-j', 'NFQUEUE', '--queue-num', '0'], check=True)
    
    # Forward all OUTPUT traffic to NFQUEUE (optional, for outbound blocking)
    # subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-j', 'NFQUEUE', '--queue-num', '0'], check=True)
    
    print("[NETWORK FIREWALL] iptables rules configured")

def cleanup_iptables():
    """Cleanup iptables rules"""
    import subprocess
    subprocess.run(['sudo', 'iptables', '-F'], check=False)
    subprocess.run(['sudo', 'iptables', '-X'], check=False)
    print("[NETWORK FIREWALL] iptables rules cleaned up")

def main():
    """Main network firewall function"""
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print("\n[NETWORK FIREWALL] Shutting down...")
        cleanup_iptables()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if running as root
    if os.geteuid() != 0:
        print("[ERROR] Network firewall must run as root (use sudo)")
        print("Run: sudo python3 network_firewall.py")
        sys.exit(1)
    
    # Setup iptables
    try:
        setup_iptables_queue()
    except Exception as e:
        print(f"[ERROR] Failed to setup iptables: {e}")
        sys.exit(1)
    
    # Create NetfilterQueue
    nfqueue = netfilterqueue.NetfilterQueue()
    nfqueue.bind(0, process_packet)
    
    print("[NETWORK FIREWALL] Starting network layer firewall...")
    print("[NETWORK FIREWALL] Listening on NFQUEUE 0")
    print("[NETWORK FIREWALL] Press Ctrl+C to stop")
    
    try:
        nfqueue.run()
    except KeyboardInterrupt:
        print("\n[NETWORK FIREWALL] Stopping...")
    finally:
        nfqueue.unbind()
        cleanup_iptables()

if __name__ == "__main__":
    main()

