
import socket
import struct
import threading
import time


class Server:
    MAGIC_COOKIE = 0xabcddcba
    OFFER_TYPE = 0x2

    def __init__(self, team_name, ip_address, udp_port, tcp_port):
        self.team_name = team_name
        self.ip_address = ip_address
        self.udp_port = udp_port
        self.tcp_port = tcp_port
        self.running = True

    def send_offers(self):
        """
        Periodically sends UDP offers ('offer' announcements).
        Step #1 and #2 in the scenario: 
          - Team Mystic and Team Valor each start their server and broadcast offers.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Enable broadcast
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # Build the offer message
            offer_message = struct.pack('!IBHH',
                                        self.MAGIC_COOKIE,
                                        self.OFFER_TYPE,
                                        self.udp_port,
                                        self.tcp_port)
            while self.running:
                # Broadcast the offer on our known UDP port
                udp_socket.sendto(offer_message, ('<broadcast>', self.udp_port))
                # For demonstration, show which server is broadcasting
                print(f"[{self.team_name}] Sending offer broadcast from {self.ip_address}")
                time.sleep(1)

    def handle_tcp_connection(self, conn, addr):
        """
        Handles an incoming TCP connection from clients requesting a file.
        Step #8: 
         - Server responds over TCP with the requested file size and then hangs up.
        """
        try:
            data = conn.recv(1024).decode()
            file_size = int(data.strip())
            # Simulate sending file_size bytes. 
            # Real code would chunk this out carefully to avoid memory spikes.
            conn.sendall(b'X' * file_size) 
        finally:
            conn.close()
    def _udp_send_file(self, udp_socket, client_addr, file_size):
        """
        Sends the requested 'file_size' in 4-byte sequence + data chunk packets.
        Each packet layout: [seq_num:4 bytes] + [raw_data].
        """
        chunk_size = 1024
        total_packets = (file_size + chunk_size - 1) // chunk_size

        offset = 0
        for seq_num in range(total_packets):
            chunk_len = min(chunk_size, file_size - offset)
            chunk = b'X' * chunk_len  # Simulated file data

            # Build packet: 4-byte big-endian sequence + chunk
            packet = struct.pack('!I', seq_num) + chunk
            udp_socket.sendto(packet, client_addr)

            offset += chunk_len
            
    def handle_udp_connection(self, udp_socket):
        """
        Waits for incoming UDP requests, which contain a 4-byte file-size integer.
        Spawns a thread to send that file in numbered packets.
        """
        while self.running:
            data, client_addr = udp_socket.recvfrom(1024)
            if len(data) < 4:
                # Invalid request
                continue

            file_size_req = struct.unpack('!I', data[:4])[0]
            # Spawn a thread to send the file to this client
            threading.Thread(
                target=self._udp_send_file,
                args=(udp_socket, client_addr, file_size_req),
                daemon=True
            ).start()

    def start(self):
        """
        Starts the server's threads:
         - One thread for broadcasting UDP offers
         - One TCP socket listening for connections
         - One UDP socket listening for incoming requests
        """
        print(f"[{self.team_name}] Server started, listening on IP address {self.ip_address}")

        # Thread to broadcast offers
        threading.Thread(target=self.send_offers, daemon=True).start()

        # TCP listener
        tcp_thread = threading.Thread(target=self._tcp_listener, daemon=True)
        tcp_thread.start()

        # UDP listener
        udp_thread = threading.Thread(target=self._udp_listener, daemon=True)
        udp_thread.start()

    def _tcp_listener(self):
        """TCP listener loop."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            # For illustration, bind to '' which means all interfaces. 
            # Real code would bind specifically to self.ip_address or a container IP.
            tcp_socket.bind(('', self.tcp_port))
            tcp_socket.listen()
            print(f"[{self.team_name}] Now listening on TCP port {self.tcp_port}")
            
            while self.running:
                conn, addr = tcp_socket.accept()
                print(f"[{self.team_name}] Accepted TCP connection from {addr}")
                threading.Thread(target=self.handle_tcp_connection, args=(conn, addr), daemon=True).start()

    def _udp_listener(self):
        """UDP listener loop."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Bind to our known UDP port
            udp_socket.bind(('', self.udp_port))
            print(f"[{self.team_name}] Now listening on UDP port {self.udp_port}")
            
            while self.running:
                self.handle_udp_connection(udp_socket)