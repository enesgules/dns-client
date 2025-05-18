# DNS Client in Python

This is a minimal DNS client built from scratch in Python using raw sockets and binary packet manipulation. It sends a DNS query to a public DNS server (like Google’s `8.8.8.8`) and parses the response to extract IPv4 addresses (A records).

## 🚀 Features

* Manually constructs DNS query packets (no DNS libraries)
* Parses raw binary responses
* Extracts and prints A records
* Measures round-trip query time

## 🧠 Learning Goals

* Understand DNS protocol internals and binary structure
* Practice low-level socket programming (UDP)
* Gain experience in working with binary data using Python’s `struct` module

## 🛠 Usage

```bash
python dns_client.py example.com
```

### Example Output

```bash
IP addresses for google.com: ['142.250.186.14']
Query time: 37 ms
```

## 🗂 Implementation Plan

### 1. Setup

* Create a Python file named `dns_client.py`
* Import required modules: `socket`, `struct`, `time`, `sys`

### 2. Construct DNS Query Packet

* Build the DNS header:

  * Transaction ID: 2 random bytes
  * Flags: standard query, recursion desired
  * QDCOUNT = 1, others = 0
* Construct the question section:

  * Convert domain name to DNS format (`example.com` → `7example3com0`)
  * QTYPE = A (1), QCLASS = IN (1)

### 3. Send DNS Packet

* Use a UDP socket (`AF_INET`, `SOCK_DGRAM`)
* Send the packet to `8.8.8.8:53`
* Record start time before sending and end time after receiving

### 4. Receive and Parse Response

* Read response from socket
* Parse the header and skip the question section
* For each answer, if type is A (IPv4):

  * Extract and convert the 4-byte RDATA into dotted decimal format

### 5. Display Results

* Print list of IPv4 addresses
* Print round-trip query time in milliseconds

## 📁 File Structure

* `dns_client.py` – Main script

## 📚 References

* [RFC 1035](https://datatracker.ietf.org/doc/html/rfc1035): Domain Names - Implementation and Specification

## ⚠️ Disclaimer

This is a learning tool and not intended for production use.
