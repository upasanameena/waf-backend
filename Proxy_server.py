from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib import parse
import re
import numpy as np
import pickle
import csv
import threading
import time
import os

# List of suspicious keywords - SQL injection and XSS patterns
badwords = [
    # SQL Injection keywords
    'select', 'union', 'or', 'and', 'where', 'from', 'insert', 'update', 'delete',
    'drop', 'table', 'database', 'exec', 'execute', 'script', 'waitfor', 'delay',
    'sleep', 'order by', 'group by', 'having', 'join', 'inner join', 'outer join',
    # XSS and Scripting
    'script', '<script', '</script>', 'javascript:', 'onerror', 'onclick', 'onload',
    'alert', 'eval', 'document.cookie', 'document.write',
    # Other suspicious patterns
    'admin', 'uid', 'password', 'passwd', 'root', 'system', 'cmd', 'command',
    'shell', 'phpinfo', 'base64', 'char(', 'ascii('
]

MODEL_PATH = 'training_model.pkl'
MALICIOUS_CSV = 'malicious_payloads.csv'
BENIGN_CSV = 'benign_payloads.csv'

# Load trained model once
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# IMPORTANT:
# For retraining, you need your vectorizer or feature extractor.
# Your current code uses ExtractFeatures returning a fixed vector,
# so no vectorizer needed; you can retrain directly on features.
# We'll add a simple retrain function below.

def ExtractFeatures(path, body):
    path = str(path)
    body = str(body)
    combined_raw = path + body
    raw_percentages = combined_raw.count("%")
    raw_spaces = combined_raw.count(" ")

    raw_percentages_count = raw_percentages if raw_percentages > 3 else 0
    raw_spaces_count = raw_spaces if raw_spaces > 3 else 0

    path_decoded = parse.unquote_plus(path)
    body_decoded = parse.unquote_plus(body)

    single_q = path_decoded.count("'") + body_decoded.count("'")
    double_q = path_decoded.count('"') + body_decoded.count('"')
    dashes = path_decoded.count("--") + body_decoded.count("--")
    braces = path_decoded.count("(") + body_decoded.count("(")
    spaces = path_decoded.count(" ") + body_decoded.count(" ")
    semicolons = path_decoded.count(";") + body_decoded.count(";")
    angle_brackets = path_decoded.count("<") + path_decoded.count(">") + body_decoded.count("<") + body_decoded.count(">")
    special_chars = sum(path_decoded.count(c) + body_decoded.count(c) for c in '$&|')
    badwords_count = sum(path_decoded.lower().count(word) + body_decoded.lower().count(word) for word in badwords)
    path_length = len(path_decoded)
    body_length = len(body_decoded)

    return [single_q, double_q, dashes, braces, spaces, raw_percentages_count,
            semicolons, angle_brackets, special_chars, path_length, body_length, badwords_count]

# --------------------- Heuristic detectors ---------------------
SQL_PATTERNS = [
    r"(?i)\bunion\s+select\b",
    r"(?i)'\s*or\s*'1'='1",
    r"(?i)or\s+1=1",
    r"(?i)order\s+by\s+\d+",
    r"(?i);?\s*drop\s+table",
]
XSS_PATTERNS = [
    r"(?i)<script[^>]*>",
    r"(?i)javascript:\s*",
    r"(?i)onerror\s*=",
    r"(?i)onload\s*=",
]
RCE_PATTERNS = [
    r"(?i)(;|&&|\|\|)\s*(sh|bash|cmd|powershell)\b",
    r"(?i)\b(system|exec|popen|passthru)\s*\(",
]
FILE_INCLUSION_PATTERNS = [
    r"(?i)(\.|\/){2,}",            # ../ traversal
    r"(?i)\b(file|php|data|zip|expect)://",
]
SSRF_PATTERNS = [
    r"(?i)\b(127\.0\.0\.1|0\.0\.0\.0|169\.254\.|localhost|\[::1\])\b",
    r"(?i)\bhttp(s)?://metadata/",
]
IDOR_HINTS = [
    r"(?i)\b(user|account|id|uid)=\d{3,}\b",
]

def find_matches(text: str, patterns):
    hits = []
    for p in patterns:
        if re.search(p, text):
            hits.append(p)
    return hits

def parse_body(content_type: str, raw: bytes) -> str:
    try:
        text = raw.decode('utf-8', errors='ignore')
    except Exception:
        return ""
    if not content_type:
        return text
    ct = content_type.lower()
    if 'application/json' in ct:
        # keep as raw JSON string for keyword scans
        return text
    if 'multipart/form-data' in ct:
        # collapse boundaries and headers, keep field names and values
        return re.sub(r"\r?\n--[-A-Za-z0-9_='\"]+\r?\n", " ", text)
    # x-www-form-urlencoded or others: return as-is
    return text

def append_payload_to_csv(file_path, path, body):
    features = ExtractFeatures(path, body)
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Store the raw path and body, plus features as backup
        writer.writerow([path, body] + features)

# Function to load data from CSV and prepare for retraining
def load_data_from_csv(file_path, label):
    data = []
    labels = []
    if not os.path.exists(file_path):
        return data, labels
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            path = row[0]
            body = row[1]
            features = ExtractFeatures(path, body)
            data.append(features)
            labels.append(label)
    return data, labels

# Retrain function - retrains model using all data in CSVs
def retrain_model():
    global model
    while True:
        time.sleep(60)  # retrain every 60 seconds

        benign_data, benign_labels = load_data_from_csv(BENIGN_CSV, 0)
        malicious_data, malicious_labels = load_data_from_csv(MALICIOUS_CSV, 1)

        X = benign_data + malicious_data
        y = benign_labels + malicious_labels

        if not X:
            print("No data available for retraining.")
            continue

        X_np = np.array(X)
        y_np = np.array(y)

        try:
            # For scikit-learn models that support partial_fit:
            if hasattr(model, 'partial_fit'):
                model.partial_fit(X_np, y_np)
            else:
                # If no partial_fit, fully retrain (assuming model supports fit)
                model.fit(X_np, y_np)

            # Save updated model
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump(model, f)

            print(f"[RETRAIN] Model retrained with {len(X)} samples "
                  f"(Benign: {len(benign_data)}, Malicious: {len(malicious_data)})")

        except Exception as e:
            print(f"Error during retrain: {e}")

class WAFServer(SimpleHTTPRequestHandler):

    def do_GET(self):
        path = self.path
        body = ""  # GET requests don't have a body

        # Extract features and check model
        features = np.array(ExtractFeatures(path, body)).reshape(1, -1)
        prediction = model.predict(features)[0]
        
        # Get prediction probability for better detection
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)[0]
            malicious_prob = proba[1] if len(proba) > 1 else proba[0]
        else:
            malicious_prob = 0.5 if prediction == 1 else 0.0

        # Check badwords (case-insensitive)
        path_lower = path.lower()
        found_badwords = [word for word in badwords if word.lower() in path_lower]
        
        # Additional SQL injection pattern detection
        found_sql_patterns = find_matches(path_lower, SQL_PATTERNS)

        # Additional security categories
        rce_hits = find_matches(path_lower, RCE_PATTERNS)
        fi_hits = find_matches(path_lower, FILE_INCLUSION_PATTERNS)
        ssrf_hits = find_matches(path_lower, SSRF_PATTERNS)
        idor_hits = find_matches(path_lower, IDOR_HINTS)

        # Combine all detection methods
        is_malicious = (
            (prediction == 1)
            or found_badwords
            or found_sql_patterns
            or rce_hits or fi_hits or ssrf_hits or idor_hits
            or (malicious_prob > 0.7)
        )

        # Append payload to respective CSV
        if is_malicious:
            append_payload_to_csv(MALICIOUS_CSV, path, body)
            
            # Build detailed reason
            reasons = []
            if found_badwords:
                reasons.append(f"Badwords: {', '.join(found_badwords)}")
            if found_sql_patterns:
                reasons.append(f"SQL pattern: {', '.join(found_sql_patterns)}")
            if prediction == 1:
                reasons.append(f"ML model (confidence: {malicious_prob:.2%})")
            if rce_hits:
                reasons.append("RCE pattern")
            if fi_hits:
                reasons.append("LFI/RFI pattern")
            if ssrf_hits:
                reasons.append("SSRF pattern")
            if idor_hits:
                reasons.append("IDOR hint")
            if not reasons:
                reasons.append("High ML confidence")
            
            reason = " | ".join(reasons) if reasons else "Malicious pattern detected"
            
            self.send_response(403, "Forbidden")
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Malicious request detected!\nReason: {reason}".encode())
            print(f"[BLOCKED] {self.client_address[0]} {path}")
            print(f"  └─ Reason: {reason}")
        else:
            # Append benign payload
            append_payload_to_csv(BENIGN_CSV, path, body)

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Nothing malicious detected. PASSED!")
            print(f"[PASSED] {self.client_address[0]} {path} (ML: {prediction}, Prob: {malicious_prob:.2%})")

    def do_POST(self):
        # Get the path
        path = self.path
        
        # Get content length & type
        content_length = int(self.headers.get('Content-Length', 0))
        content_type = self.headers.get('Content-Type', '')
        
        # Read the request body (payload)
        raw_body = self.rfile.read(content_length)
        body = parse_body(content_type, raw_body)
        
        # Extract features and check model
        features = np.array(ExtractFeatures(path, body)).reshape(1, -1)
        prediction = model.predict(features)[0]
        
        # Get prediction probability for better detection
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)[0]
            malicious_prob = proba[1] if len(proba) > 1 else proba[0]
        else:
            malicious_prob = 0.5 if prediction == 1 else 0.0

        # Check badwords in both path and body (case-insensitive)
        path_lower = path.lower()
        body_lower = body.lower()
        combined_text = path_lower + " " + body_lower
        
        found_badwords = [word for word in badwords if word.lower() in combined_text]
        
        # Additional SQL injection pattern detection
        found_sql_patterns = find_matches(combined_text, SQL_PATTERNS)
        
        # XSS pattern detection in body
        found_xss_patterns = find_matches(body_lower, XSS_PATTERNS)

        # Other classes
        rce_hits = find_matches(combined_text, RCE_PATTERNS)
        fi_hits = find_matches(combined_text, FILE_INCLUSION_PATTERNS)
        ssrf_hits = find_matches(combined_text, SSRF_PATTERNS)
        idor_hits = find_matches(combined_text, IDOR_HINTS)

        # Combine all detection methods
        is_malicious = (
            (prediction == 1)
            or found_badwords or found_sql_patterns or found_xss_patterns
            or rce_hits or fi_hits or ssrf_hits or idor_hits
            or (malicious_prob > 0.7)
        )

        # Append payload to respective CSV
        if is_malicious:
            append_payload_to_csv(MALICIOUS_CSV, path, body)
            
            # Build detailed reason
            reasons = []
            if found_badwords:
                reasons.append(f"Badwords: {', '.join(found_badwords)}")
            if found_sql_patterns:
                reasons.append(f"SQL pattern: {', '.join(found_sql_patterns)}")
            if found_xss_patterns:
                reasons.append(f"XSS pattern: {', '.join(found_xss_patterns)}")
            if prediction == 1:
                reasons.append(f"ML model (confidence: {malicious_prob:.2%})")
            if rce_hits:
                reasons.append("RCE pattern")
            if fi_hits:
                reasons.append("LFI/RFI pattern")
            if ssrf_hits:
                reasons.append("SSRF pattern")
            if idor_hits:
                reasons.append("IDOR hint")
            if not reasons:
                reasons.append("High ML confidence")
            
            reason = " | ".join(reasons) if reasons else "Malicious payload detected"
            
            self.send_response(403, "Forbidden")
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Malicious payload detected!\nReason: {reason}".encode())
            print(f"[BLOCKED POST] {self.client_address[0]} {path}")
            print(f"  └─ Payload: {body[:100]}..." if len(body) > 100 else f"  └─ Payload: {body}")
            print(f"  └─ Reason: {reason}")
        else:
            # Append benign payload
            append_payload_to_csv(BENIGN_CSV, path, body)

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Nothing malicious detected. PASSED!")
            print(f"[PASSED POST] {self.client_address[0]} {path} (ML: {prediction}, Prob: {malicious_prob:.2%})")

if __name__ == "__main__":
    # Start retrain thread
    retrain_thread = threading.Thread(target=retrain_model, daemon=True)
    retrain_thread.start()

    # Use port 8081 to avoid conflict with UI server (8080)
    # You can change this if needed
    host, port = '127.0.0.1', 8081
    print(f"Starting WAF server on http://{host}:{port}")
    print(f"Note: UI server runs on port 8080, WAF runs on port {port}")
    server = HTTPServer((host, port), WAFServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()
