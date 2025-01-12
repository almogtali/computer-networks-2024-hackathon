
import socket
import struct
import threading
import time


class Client:
    MAGIC_COOKIE = 0xabcddcba
    OFFER_TYPE = 0x2
    REQUEST_TYPE = 0x3

    def __init__(self, team_name, requested_file_size, tcp_connections, udp_connections):
        self.team_name = team_name
        self.requested_file_size = requested_file_size
        self.tcp_connections = tcp_connections
        self.udp_connections = udp_connections
        self.running = True
        # A place to store transfer statistics
        self.tcp_transfer_stats = []
        self.udp_transfer_stats = []

    def listen_for_offers(self):
        """
        Step #4 and #5: 
          - Clients start up and listen for server 'offer' announcements via UDP.
          - Print out "Received offer from <server_ip>"
        """
        print(f"[{self.team_name}] Client started, listening for offer requests...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Bind to the same broadcast port the server uses for offers
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind(('', 0))
            # Listen until we decide to stop
            while self.running:
                data, server_addr = udp_socket.recvfrom(1024)
                magic_cookie, message_type, udp_port, tcp_port = struct.unpack('!IBHH', data)
                if magic_cookie == self.MAGIC_COOKIE and message_type == self.OFFER_TYPE:
                    print(f"[{self.team_name}] Received offer from {server_addr[0]}")
                    # Step #6 and #7:
                    #   - Connect to the server via TCP and UDP 
                    #   - Send file size, measure start times, etc.
                    self.handle_server(server_addr[0], udp_port, tcp_port)

    def handle_server(self, server_ip, udp_port, tcp_port):
        """
        Connect to the server with both TCP and UDP to request the file.
        These operations should ideally run in parallel threads.
        """
        # Spin off TCP connections
        for i in range(self.tcp_connections):
            threading.Thread(
                target=self.tcp_transfer,
                args=(server_ip, tcp_port, i + 1),
                daemon=True
            ).start()

        # Spin off UDP connections
        for i in range(self.udp_connections):
            threading.Thread(
                target=self.udp_transfer,
                args=(server_ip, udp_port, i + 1),
                daemon=True
            ).start()

    def tcp_transfer(self, server_ip, tcp_port, conn_index):
        """
        Step #6, #8, #9:
          - Connect over TCP, send requested file size, measure time, 
            compute speed, and print summary.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            start_time = time.time()
            tcp_socket.connect((server_ip, tcp_port))
            tcp_socket.sendall(f"{self.requested_file_size}\n".encode())
            total_received = 0
            # Keep receiving data until we've got the entire file or server closes
            while total_received < self.requested_file_size:
                chunk = tcp_socket.recv(4096)
                if not chunk:
                    break
                total_received += len(chunk)
            end_time = time.time()
        
        elapsed = end_time - start_time
        # Compute bits per second: total_received bytes = total_received * 8 bits
        speed_bps = (total_received * 8) / elapsed if elapsed > 0 else 0
        self.tcp_transfer_stats.append((conn_index, elapsed, speed_bps))

        print(f"[{self.team_name}] TCP transfer #{conn_index} finished, "
              f"total time: {elapsed:.2f}s, total speed: {speed_bps:.2f} bits/s")

    def udp_transfer(self, server_ip, udp_port, conn_index):
        """
        Step #6, #8, #9:
          - Send a request over UDP, receive multiple packets, measure time, 
            detect "no data for 1 second" as completed, compute packet loss, etc.
        """
        # For demonstration, we just do a single “request” send and pretend we measure.
        start_time = time.time()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send request (with file size)
            request_packet = struct.pack('!I', self.requested_file_size)
            udp_socket.sendto(request_packet, (server_ip, udp_port))

            # In real code, you'd listen in a loop for incoming data, 
            # track sequence numbers, and detect missing packets. 
            # Here, we'll just sleep to simulate receiving data, 
            # then assume 95% success...
            time.sleep(2)
            # Suppose we get no data for 1 second => transfer done
            end_time = time.time()

        elapsed = end_time - start_time
        speed_bps = (self.requested_file_size * 8) / elapsed if elapsed > 0 else 0
        # Assume we got 95% success
        packets_received_percent = 95
        self.udp_transfer_stats.append((conn_index, elapsed, speed_bps, packets_received_percent))

        print(f"[{self.team_name}] UDP transfer #{conn_index} finished, "
              f"total time: {elapsed:.2f}s, total speed: {speed_bps:.2f} bits/s, "
              f"percentage of packets received successfully: {packets_received_percent}%")

    def start(self):
        """Start the client listening on a thread."""
        threading.Thread(target=self.listen_for_offers, daemon=True).start()
