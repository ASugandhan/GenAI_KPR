"""
ZeroTrust AI — Traffic Simulator
Generates realistic synthetic network packets (normal + attack traffic).
Used for ML training and real-time demo streaming.
"""
import random
import time
from datetime import datetime


ATTACK_TYPES = ["normal", "brute_force", "port_scan", "ddos", "exploit", "c2_beacon"]
PROTOCOLS = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "DNS", "SSH"]

INTERNAL_IPS = [f"192.168.1.{i}" for i in range(10, 60)]
EXTERNAL_IPS = [f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(30)]
GATEWAY_IPS = ["10.0.0.1", "192.168.1.1"]

ATTACK_PROFILES = {
    "brute_force": {
        "ports": [22, 3389, 21],
        "protocols": ["SSH", "TCP"],
        "bytes_range": (500, 5000),
        "duration_range": (0.01, 0.5),
        "packet_count_range": (100, 2000),
    },
    "port_scan": {
        "ports": list(range(1, 1024)),
        "protocols": ["TCP", "UDP"],
        "bytes_range": (40, 200),
        "duration_range": (0.001, 0.1),
        "packet_count_range": (1, 5),
    },
    "ddos": {
        "ports": [80, 443, 8080],
        "protocols": ["TCP", "UDP", "HTTP"],
        "bytes_range": (10000, 100000),
        "duration_range": (0.1, 2.0),
        "packet_count_range": (5000, 50000),
    },
    "exploit": {
        "ports": [80, 443, 8443, 3306, 5432],
        "protocols": ["HTTP", "HTTPS", "TCP"],
        "bytes_range": (2000, 30000),
        "duration_range": (0.5, 5.0),
        "packet_count_range": (10, 200),
    },
    "c2_beacon": {
        "ports": [443, 8443, 53],
        "protocols": ["HTTPS", "DNS"],
        "bytes_range": (100, 1500),
        "duration_range": (0.01, 0.1),
        "packet_count_range": (1, 10),
    },
}

NORMAL_PROFILE = {
    "ports": [80, 443, 53, 8080, 3000, 5000],
    "protocols": ["HTTP", "HTTPS", "DNS", "TCP"],
    "bytes_range": (64, 15000),
    "duration_range": (0.01, 3.0),
    "packet_count_range": (1, 100),
}


def generate_packet(attack_type=None, attack_probability=0.15):
    """Generate a single synthetic network packet."""
    if attack_type is None:
        if random.random() < attack_probability:
            attack_type = random.choice(ATTACK_TYPES[1:])  # skip 'normal'
        else:
            attack_type = "normal"

    if attack_type == "normal":
        profile = NORMAL_PROFILE
    else:
        profile = ATTACK_PROFILES[attack_type]

    src_ip = random.choice(EXTERNAL_IPS if attack_type != "normal" else INTERNAL_IPS)
    dst_ip = random.choice(INTERNAL_IPS if attack_type != "normal" else EXTERNAL_IPS)

    packet = {
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "port": random.choice(profile["ports"]),
        "protocol": random.choice(profile["protocols"]),
        "bytes": random.randint(*profile["bytes_range"]),
        "duration": round(random.uniform(*profile["duration_range"]), 4),
        "packet_count": random.randint(*profile["packet_count_range"]),
        "timestamp": datetime.utcnow().isoformat(),
        "attack_type": attack_type,
    }
    return packet


def generate_training_data(n_samples=5000, attack_ratio=0.3):
    """Generate a labeled dataset for ML training."""
    data = []
    n_attacks = int(n_samples * attack_ratio)
    n_normal = n_samples - n_attacks

    for _ in range(n_normal):
        data.append(generate_packet(attack_type="normal"))

    for _ in range(n_attacks):
        atype = random.choice(ATTACK_TYPES[1:])
        data.append(generate_packet(attack_type=atype))

    random.shuffle(data)
    return data


def stream_packets(packets_per_second=2, attack_probability=0.15):
    """Generator that yields packets at a steady rate (for SSE)."""
    while True:
        yield generate_packet(attack_probability=attack_probability)
        time.sleep(1.0 / packets_per_second)
