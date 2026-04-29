# Secure Remote Desktop with Dual-Channel TLS + Mutual TLS Authentication

## Overview

This project is a **secure remote desktop prototype** built in Python that provides encrypted screen sharing and protected remote input control over two separate secure channels.

Lab topology used:

Host Laptop: `192.168.56.2`
Client Laptop: `192.168.56.5`

Communication uses two dedicated ports:

* **Port 5000** — Secure screen streaming channel
* **Port 5001** — Secure remote input control channel

Both channels are independently protected using **TLS**, and the system uses **Mutual TLS (mTLS)** so both client and host authenticate each other before a session starts.

This design provides:

* Confidential encrypted transport
* Mutual endpoint authentication
* Protection against **Man-in-the-Middle (MITM) attacks**
* Integrity protection against tampering
* Channel separation for stronger security architecture

---

# Architecture

## Dual-Channel Secure Architecture

```text
Client (192.168.56.5)                        Host (192.168.56.2)
─────────────────────                        ───────────────────

Port 5000 ───── TLS 1.3 ───────────────────► Secure Screen Stream

Port 5001 ───── mTLS Secure Channel ───────► Mouse + Keyboard Control


Both channels encrypted independently
Both channels authenticated
Session protected through token validation
```
# Certificate Generation (OpenSSL)

This project uses **Mutual TLS (mTLS)** with a self-managed Certificate Authority (CA).

Certificates were generated using **OpenSSL**.

## Generate Certificate Authority (CA)

Create CA private key:

```bash id="c1"
openssl genrsa -out ca_key.pem 4096
```

Generate CA certificate:

```bash id="c2"
openssl req -x509 -new -nodes -key ca_key.pem -sha256 -days 365 \
-out ca_cert.pem
```

---

# Generate Host Certificate

Generate host private key:

```bash id="c3"
openssl genrsa -out host_key.pem 4096
```

Generate certificate signing request:

```bash id="c4"
openssl req -new -key host_key.pem -out host.csr
```

Sign host certificate with CA:

```bash id="c5"
openssl x509 -req -in host.csr \
CA ca_cert.pem -CAkey ca_key.pem \
-CAcreateserial -out host_cert.pem \
-days 365 -sha256
```

---

# Generate Client Certificate

Generate client private key:

```bash id="c6"
openssl genrsa -out client_key.pem 4096
```

Generate client CSR:

```bash id="c7"
openssl req -new -key client_key.pem -out client.csr
```

Sign client certificate:

```bash id="c8"
openssl x509 -req -in client.csr \
-CA ca_cert.pem -CAkey ca_key.pem \
-CAcreateserial -out client_cert.pem \
-days 365 -sha256
```

---

# Certificate Layout

```bash id="c9"
certs/
├── ca_cert.pem
├── ca_key.pem
├── host_cert.pem
├── host_key.pem
├── client_cert.pem
└── client_key.pem
```

---

# Mutual TLS Verification Configuration

Host verifies client certificate:

```python id="c10"
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations("ca_cert.pem")
```

Client verifies host certificate:

```python id="c11"
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations("ca_cert.pem")
```

Both endpoints present certificates during TLS handshake.

---

# Verify Certificates

Check host certificate:

```bash id="c12"
openssl x509 -in host_cert.pem -text -noout
```

Check client certificate:

```bash id="c13"
openssl x509 -in client_cert.pem -text -noout
```

Verify certificate chain:

```bash id="c14"
openssl verify -CAfile ca_cert.pem host_cert.pem
openssl verify -CAfile ca_cert.pem client_cert.pem
```

Expected:

```text id="c15"
host_cert.pem: OK
client_cert.pem: OK
```

---

# Security Benefit

Using CA-signed certificates with mTLS provides:

* Endpoint authentication
* Trusted certificate validation
* Protection against rogue clients/servers
* Resistance against Man-in-the-Middle (MITM) attacks

Only systems possessing valid CA-signed certificates can establish a session.

---

# Security Features

## 1. TLS Encryption on Both Ports

Both channels are wrapped with TLS:

* Port 5000 → encrypted video frames
* Port 5001 → encrypted control events

All traffic captured in packet analysis appears encrypted.

---

## 2. Mutual TLS Authentication (mTLS)

Both systems authenticate each other using certificates signed by a trusted Certificate Authority.

Authentication flow:

```text
Client presents certificate  → Host verifies
Host presents certificate    → Client verifies

Trusted CA validates both sides
Session established only if both succeed
```

### Security Benefit

This prevents:

* Unauthorized client access
* Rogue host impersonation
* Session hijacking
* Certificate spoofing
* **Man-in-the-Middle (MITM) attacks**

If an attacker attempts interception with a fake certificate:

* TLS handshake fails
* Connection is rejected
* Session does not start

---

## 3. Secure Remote Input Control

Dedicated control channel supports:

* Mouse movement
* Mouse clicks
* Keyboard input

Security controls:

* Separate encrypted channel
* Session token validation
* TLS protected input events
* No plaintext keystrokes or mouse events visible in packet captures

Port:
`5001`

---

# Security Design

## Confidentiality

All sensitive traffic is encrypted:

* Screen frames
* Keyboard events
* Mouse movements
* Session tokens

Implemented using:

* TLS 1.3
* Mutual TLS authentication

---

## Authentication

Authentication occurs at two levels:

### Endpoint Authentication

Mutual TLS verifies:

* Client identity
* Host identity

### Session Authentication

Session tokens validate authorized control events.

---

## Integrity

TLS authenticated encryption protects against:

* Packet tampering
* Modified control events
* Stream manipulation

Any altered traffic fails cryptographic validation.

---

## Separation of Channels

Video and control use separate ports:

| Channel          | Port | Purpose            |
| ---------------- | ---- | ------------------ |
| Screen Streaming | 5000 | Remote display     |
| Input Control    | 5001 | Mouse and keyboard |

Benefits:

* Reduced attack surface
* Modular design
* Channel isolation
* Easier monitoring and debugging

---

# Packet Analysis Validation

Traffic security was verified using packet capture analysis.

Tools used:

* Wireshark
* tcpdump

## Verified Observations

### Port 5000 (Screen Stream)

Observed:

* TLS handshake packets
* Encrypted Application Data records
* No visible image/frame data in plaintext

---

### Port 5001 (Input Control)

Observed:

* TLS encrypted input traffic
* No visible keyboard events
* No visible mouse coordinates in plaintext

---

## Example Validation Commands

```bash id="m1"
sudo tcpdump -A -i <interface> port 5000
```

```bash id="m2"
sudo tcpdump -A -i <interface> port 5001
```

Wireshark analysis confirmed both channels carry encrypted TLS payloads.

---

# Technologies Used

* Python 3
* OpenCV
* MSS
* NumPy
* PyAutoGUI
* pynput
* Python ssl module
* TLS 1.3
* Mutual TLS (mTLS)
* Wireshark
* tcpdump
* VirtualBox lab environment

---

# Running the Project

## On Host

```bash id="m4"
python3 host.py
```

---

## On Client

```bash id="m5"
python3 client.py
```

If certificate validation succeeds:

* Screen streaming starts on port 5000
* Secure input control starts on port 5001

---

# Security Improvements Achieved

| Before                       | After                            |
| ---------------------------- | -------------------------------- |
| Unverified connections       | Mutual TLS verification          |
| Plain trust model            | CA-based trust                   |
| Manual authentication        | Certificate authentication       |
| Potential MITM exposure      | MITM-resistant design            |
| Single-channel remote access | Dual secure-channel architecture |

---

# Why This Project Matters

This project demonstrates practical implementation of:

* Secure transport design
* Remote access hardening
* Mutual TLS authentication
* MITM defense mechanisms
* Traffic encryption validation
* Secure channel separation

It combines networking, cryptography, packet analysis, and defensive security engineering in one practical lab project.

---

# Future Improvements

Possible next phases:

* Diffie-Hellman challenge-response
* TOTP / OTP approval
* File transfer over secure channel
* Multi-client support
* Logging and SIEM integration
* Intrusion detection monitoring
* Screen delta optimization

---

# Disclaimer

Educational and authorized lab use only.

Use only on systems you own or have permission to test.

---

## Author

Suresh Bhanuka
Cybersecurity Undergraduate | Defensive Security Enthusiast


