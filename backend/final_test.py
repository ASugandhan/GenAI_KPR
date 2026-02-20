import requests
import json
import time

BASE_URL = "http://localhost:8080/api"
CREDS = {"username": "admin", "password": "zerotrust123"}

def run_tests():
    results = {}
    session = requests.Session()
    
    # --- PHASE 1: Authentication ---
    try:
        resp = session.post(f"{BASE_URL}/auth/login", json=CREDS)
        token = resp.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        results["2.1 Valid Login"] = "PASS" if token else "FAIL"
    except Exception as e:
        print(f"Login failed: {e}")
        return
        
    # --- PHASE 2: System Health ---
    results["1.3 Health Endpoint"] = "PASS" if session.get(f"{BASE_URL}/health").status_code == 200 else "FAIL"
    
    # --- PHASE 3: Threat Detection ---
    bf_payload = {"src_ip":"192.168.1.45","dst_ip":"10.0.0.1","port":22,"protocol":"TCP","bytes":8420,"duration":0.3,"packet_count":847}
    normal_payload = {"src_ip":"192.168.1.50","dst_ip":"10.0.0.1","port":80,"protocol":"TCP","bytes":1200,"duration":0.1,"packet_count":3}
    ddos_payload = {"src_ip":"192.168.1.77","dst_ip":"10.0.0.1","port":80,"protocol":"TCP","bytes":1500000,"duration":0.1,"packet_count":9999}
    
    results["3.1 Brute Force"] = "PASS" if session.post(f"{BASE_URL}/detect", json=bf_payload).json().get("is_threat") else "FAIL"
    results["3.2 Normal Traffic"] = "PASS" if not session.post(f"{BASE_URL}/detect", json=normal_payload).json().get("is_threat") else "FAIL"
    results["3.3 DDoS Pattern"] = "PASS" if session.post(f"{BASE_URL}/detect", json=ddos_payload).json().get("is_threat") else "FAIL"
    
    # --- PHASE 4: Trust Scores ---
    trust = session.get(f"{BASE_URL}/trust").json()
    results["4.1 Get All Scores"] = "PASS" if len(trust.get("devices", [])) > 0 else "FAIL"
    
    # --- PHASE 5: Rules ---
    rules = session.get(f"{BASE_URL}/rules").json()
    results["5.1 Get All Rules"] = "PASS" if isinstance(rules, list) else "FAIL"
    results["5.2 Rule Generated"] = "PASS" if len(rules) > 0 else "FAIL"
    
    # --- PHASE 7: Analyst ---
    sum_resp = session.post(f"{BASE_URL}/summarize", json={"time_window":"1h","format":"analyst"})
    results["7.1 Summarize"] = "PASS" if sum_resp.status_code == 200 else "FAIL"
    
    sh_resp = session.post(f"{BASE_URL}/selfheal", json={"incident_id":"test-001","severity":"HIGH"})
    results["7.3 Self-heal"] = "PASS" if sh_resp.status_code == 200 else "FAIL"
    
    # --- PHASE 8: Logs ---
    logs = session.get(f"{BASE_URL}/logs").json()
    results["8.1 Get Logs"] = "PASS" if len(logs.get("events", [])) > 0 else "FAIL"
    
    # --- PHASE 10: MySQL ---
    import pymysql
    try:
        conn = pymysql.connect(host='localhost', user='root', password='Sugandhan@10163', database='zerotrust_ai')
        results["10.1 MySQL Connection"] = "PASS"
        conn.close()
    except:
        results["10.1 MySQL Connection"] = "FAIL"
        
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_tests()
