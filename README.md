# DNS Client in Python

This is a minimal DNS client built from scratch in Python using raw sockets and binary packet manipulation. It sends a DNS query to a public DNS server (like Google's `8.8.8.8`) and parses the response to extract IPv4 addresses (A records).

## 🚀 Features

* Manually constructs DNS query packets (no DNS libraries)
* Parses raw binary responses
* Extracts and prints A records
* Measures round-trip query time

## 🧠 Learning Goals

* Understand DNS protocol internals and binary structure
* Practice low-level socket programming (UDP)
* Gain experience in working with binary data using Python's `struct` module

## 🛠 Usage

```bash
python dns_client.py [-v] domain_name
```

The `-v` flag enables verbose logging, which provides detailed information about the DNS query process, including:
* Transaction ID generation
* DNS header construction
* Domain name conversion
* Query packet creation
* Response parsing details
* Record type information

### Example Output

Without verbose flag:
```bash
IP addresses for google.com: ['142.250.186.14']
Query time: 37 ms
```

With verbose flag (-v):
```bash
2024-03-21 10:30:15 - DEBUG - Generated transaction ID: 12345
2024-03-21 10:30:15 - DEBUG - DNS Header - Flags: 256, QDCount: 1, ANCount: 0
2024-03-21 10:30:15 - DEBUG - Converted domain 'google.com' to DNS format: b'\x06google\x03com\x00'
2024-03-21 10:30:15 - DEBUG - Created DNS query packet for domain: google.com
2024-03-21 10:30:15 - DEBUG - Sending DNS query to 8.8.8.8:53
2024-03-21 10:30:15 - DEBUG - Waiting for DNS response...
2024-03-21 10:30:15 - DEBUG - Parsing DNS response - Transaction ID: 12345
2024-03-21 10:30:15 - DEBUG - Response counts - Questions: 1, Answers: 1, Authority: 0, Additional: 0
2024-03-21 10:30:15 - DEBUG - Found domain name pointer
2024-03-21 10:30:15 - DEBUG - Record Type: 1, Class: 1, TTL: 300, Data Length: 4
2024-03-21 10:30:15 - DEBUG - Found A record with IP: 142.250.186.14
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
