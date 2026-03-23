# find-subdomains-by-public-Certificate-

A lightweight Python tool designed to extract and list subdomains associated with a given domain by querying public Certificate Transparency logs from [crt.sh](https://crt.sh).

---

## 📜 Description

**find-subdomains-by-public-Certificates** helps security researchers and penetration testers to passively discover subdomains for a target organization by analyzing issued SSL/TLS certificates from public CT logs.  

The tool automates fetching certificate data from **crt.sh**, parsing it, and printing unique subdomains in a clean list. It’s particularly useful during the **passive reconnaissance** phase of penetration testing.

---

## ⚙️ Features
- Queries `crt.sh` for certificates issued to the target domain  
- Extracts and lists all unique subdomains  
- Removes wildcard prefixes automatically (`*.`)  
- Simple command-line interface  
- No API keys required  

---

## 🚀 Usage

### 🔧 Requirements
Install dependencies:
```bash
pip install requests

```

### 🔧 Execute

run:
```bash
python crt.py -d example.com
```

Optional timeout flag:
```bash
python crt.py -d example.com -t 20
```

Optional timeout retry flags:
```bash
python crt.py -d example.com -t 20 -r 5 --retry-backoff 1.5
```
