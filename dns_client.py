#!/usr/bin/env python3
import socket
import struct
import time
import sys
import random

def convert_domain_to_dns_format(domain):
    """Convert a domain name to DNS format (length byte + label)"""
    dns_format = b''
    for part in domain.split('.'):
        dns_format += bytes([len(part)]) + part.encode('ascii')
    dns_format += b'\x00'  # Add terminating zero
    return dns_format

def create_dns_query(domain_name, query_type=1):  # Type 1 is A record
    """Create a DNS query packet for the given domain_name"""
    
    # Generate random transaction ID
    transaction_id = random.randint(0, 65535)
    
    # DNS Header fields
    flags = 0x0100  # Standard query with recursion desired
    qdcount = 1     # One question
    ancount = 0     # No answers in query
    nscount = 0     # No authority records
    arcount = 0     # No additional records
    
    # Construct the header using struct
    header = struct.pack('!HHHHHH', 
                         transaction_id, 
                         flags, 
                         qdcount, 
                         ancount, 
                         nscount, 
                         arcount)
    
    # Construct the question section
    question = convert_domain_to_dns_format(domain_name)
    question += struct.pack('!HH', query_type, 1)  # QTYPE=A (1), QCLASS=IN (1)
    
    return header + question

def parse_dns_response(response):
    """Parse the raw DNS response and extract IPv4 addresses"""
    
    # Unpack the header
    header = struct.unpack('!HHHHHH', response[:12])
    transaction_id, flags, qdcount, ancount, nscount, arcount = header
    
    # Skip the question section (find the end of it)
    offset = 12  # Start after the header
    
    # Skip domain name in question
    while True:
        length = response[offset]
        if length == 0:
            offset += 1
            break
        offset += length + 1
    
    # Skip QTYPE and QCLASS (4 bytes)
    offset += 4
    
    # Parse answers
    ip_addresses = []
    for i in range(ancount):
        # Check if this is a pointer to a domain name
        if (response[offset] & 0xC0) == 0xC0:
            # It's a pointer, skip 2 bytes
            offset += 2
        else:
            # Skip the domain name
            while True:
                length = response[offset]
                if length == 0:
                    offset += 1
                    break
                offset += length + 1
        
        # Extract record type, class, TTL, and data length
        record_type, record_class, ttl, data_len = struct.unpack('!HHIH', response[offset:offset+10])
        offset += 10
        
        # If it's an A record (type 1), extract the IP
        if record_type == 1:  # A record
            ip_bytes = response[offset:offset+data_len]
            ip_address = '.'.join(str(b) for b in ip_bytes)
            ip_addresses.append(ip_address)
        
        # Move to the next record
        offset += data_len
    
    return ip_addresses

def dns_lookup(domain_name, dns_server='8.8.8.8', dns_port=53):
    """Perform a DNS lookup for the given domain_name"""
    
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)  # Set timeout to 5 seconds
        
        # Create DNS query
        query = create_dns_query(domain_name)
        
        # Record start time
        start_time = time.time()
        
        # Send the query
        sock.sendto(query, (dns_server, dns_port))
        
        # Receive the response
        response, _ = sock.recvfrom(512)  # DNS messages are usually <= 512 bytes
        
        # Record end time
        end_time = time.time()
        
        # Calculate query time in milliseconds
        query_time_ms = int((end_time - start_time) * 1000)
        
        # Parse the response
        ip_addresses = parse_dns_response(response)
        
        return ip_addresses, query_time_ms

def main():
    # Check if domain name is provided
    if len(sys.argv) != 2:
        print("Usage: python dns_client.py domain_name")
        sys.exit(1)
    
    domain_name = sys.argv[1]
    
    try:
        ip_addresses, query_time = dns_lookup(domain_name)
        print(f"IP addresses for {domain_name}: {ip_addresses}")
        print(f"Query time: {query_time} ms")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
