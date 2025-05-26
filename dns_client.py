#!/usr/bin/env python3
import socket
import struct
import time
import sys
import random
import logging

def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def convert_domain_to_dns_format(domain):
    """Convert a domain name to DNS format (length byte + label)"""
    dns_format = b''
    for part in domain.split('.'):
        dns_format += bytes([len(part)]) + part.encode('ascii')
    dns_format += b'\x00'  # Add terminating zero
    logging.debug(f"Converted domain '{domain}' to DNS format: {dns_format}")
    return dns_format

def create_dns_query(domain_name, query_type=1):  # Type 1 is A record
    """Create a DNS query packet for the given domain_name"""
    
    # Generate random transaction ID
    transaction_id = random.randint(0, 65535)
    logging.debug(f"Generated transaction ID: {transaction_id}")
    
    # DNS Header fields
    flags = 0x0100  # Standard query with recursion desired
    qdcount = 1     # One question
    ancount = 0     # No answers in query
    nscount = 0     # No authority records
    arcount = 0     # No additional records
    
    logging.debug(f"DNS Header - Flags: {flags}, QDCount: {qdcount}, ANCount: {ancount}")
    
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
    
    logging.debug(f"Created DNS query packet for domain: {domain_name}")
    return header + question

def parse_dns_response(response):
    """Parse the raw DNS response and extract IPv4 addresses"""
    
    # Unpack the header
    header = struct.unpack('!HHHHHH', response[:12])
    transaction_id, flags, qdcount, ancount, nscount, arcount = header
    
    logging.debug(f"Parsing DNS response - Transaction ID: {transaction_id}")
    logging.debug(f"Response counts - Questions: {qdcount}, Answers: {ancount}, Authority: {nscount}, Additional: {arcount}")
    
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
        logging.debug(f"Parsing answer record {i+1}/{ancount}")
        
        # Check if this is a pointer to a domain name
        if (response[offset] & 0xC0) == 0xC0:
            logging.debug("Found domain name pointer")
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
        
        logging.debug(f"Record Type: {record_type}, Class: {record_class}, TTL: {ttl}, Data Length: {data_len}")
        
        # If it's an A record (type 1), extract the IP
        if record_type == 1:  # A record
            ip_bytes = response[offset:offset+data_len]
            ip_address = '.'.join(str(b) for b in ip_bytes)
            ip_addresses.append(ip_address)
            logging.debug(f"Found A record with IP: {ip_address}")
        
        # Move to the next record
        offset += data_len
    
    return ip_addresses

def dns_lookup(domain_name, dns_server='8.8.8.8', dns_port=53):
    """Perform a DNS lookup for the given domain_name"""
    
    logging.info(f"Starting DNS lookup for domain: {domain_name}")
    logging.info(f"Using DNS server: {dns_server}:{dns_port}")
    
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)  # Set timeout to 5 seconds
        
        # Create DNS query
        query = create_dns_query(domain_name)
        
        # Record start time
        start_time = time.time()
        
        # Send the query
        logging.debug(f"Sending DNS query to {dns_server}:{dns_port}")
        sock.sendto(query, (dns_server, dns_port))
        
        # Receive the response
        logging.debug("Waiting for DNS response...")
        response, _ = sock.recvfrom(512)  # DNS messages are usually <= 512 bytes
        
        # Record end time
        end_time = time.time()
        
        # Calculate query time in milliseconds
        query_time_ms = int((end_time - start_time) * 1000)
        logging.info(f"DNS query completed in {query_time_ms}ms")
        
        # Parse the response
        ip_addresses = parse_dns_response(response)
        
        return ip_addresses, query_time_ms

def main():
    # Check command line arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python dns_client.py [-v] domain_name")
        sys.exit(1)
    
    # Check for verbose flag
    verbose = False
    if sys.argv[1] == '-v':
        verbose = True
        domain_name = sys.argv[2]
    else:
        domain_name = sys.argv[1]
    
    # Setup logging
    setup_logging(verbose)
    
    try:
        ip_addresses, query_time = dns_lookup(domain_name)
        print(f"IP addresses for {domain_name}: {ip_addresses}")
        print(f"Query time: {query_time} ms")
    except Exception as e:
        logging.error(f"Error during DNS lookup: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
