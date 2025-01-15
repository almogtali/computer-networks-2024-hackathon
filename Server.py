
import socket
import struct
import threading
import time
import const

class Server:
    MAGIC_COOKIE = 0xabcddcba
    OFFER_TYPE = 0x2

    COLOR_RESET = "\033[0m"
    COLOR_GREEN = "\033[92m"
    COLOR_YELLOW = "\033[93m"
    COLOR_RED = "\033[91m"
    COLOR_BLUE = "\033[94m"

    def __init__(self, team_name, ip_address):
        self.team_name = team_name
        self.ip_address = ip_address
        self.tcp_port = self.find_available_port(type_='TCP',end_port=10000)
        self.udp_port = self.find_available_port(type_='UDP',start_port=11000)
        self.running = True
        self.stats = {"tcp_requests": 0, "udp_requests": 0}

    def find_available_port(self,type_,start_port=1024, end_port=65535):
        for port in range(start_port, end_port + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
                try:
                    test_socket.bind(("localhost", port))
                    return port
                except OSError:
                    continue
        if type_ =='TCP':
            return const.def_tcp
        return const.def_udp
     
    def send_offers(self):
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
                udp_socket.sendto(offer_message, ('<broadcast>', const.port_broadcast))
                print(f"{self.COLOR_GREEN}[{self.team_name}] Sending offer broadcast from {self.ip_address}{self.COLOR_RESET}")
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
            conn.sendall(b'X' * file_size)
            self.stats["tcp_requests"] += 1
            print(f"{self.COLOR_YELLOW}[{self.team_name}] Handled TCP request from {addr}{self.COLOR_RESET}")
        except Exception as e:
            print(f"{self.COLOR_RED}[{self.team_name}] Error handling TCP request: {e}{self.COLOR_RESET}")
        finally:
            self.print_summary()
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
        self.stats["udp_requests"] += 1
            
    def handle_udp_connection(self, udp_socket):
        """
        Handles incoming UDP requests.
        """
        while self.running:
            try:
                data, client_addr = udp_socket.recvfrom(1024)
                if len(data) < 4:
                    continue

                file_size_req = struct.unpack('!I', data[:4])[0]
                threading.Thread(
                    target=self._udp_send_file,
                    args=(udp_socket, client_addr, file_size_req),
                    daemon=True
                ).start()

                print(f"{self.COLOR_YELLOW}[{self.team_name}] Handled UDP request from {client_addr}{self.COLOR_RESET}")
            except Exception as e:
                print(f"{self.COLOR_RED}[{self.team_name}] Error handling UDP request: {e}{self.COLOR_RESET}")

    def start(self):
        """
        Starts the server's threads:
         - One thread for broadcasting UDP offers
         - One TCP socket listening for connections
         - One UDP socket listening for incoming requests
        """
        print(f"{self.COLOR_GREEN}[{self.team_name}] Server started, listening on IP address {self.ip_address}{self.COLOR_RESET}")


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
            print(f"{self.COLOR_BLUE}[{self.team_name}] Listening on TCP port {self.tcp_port}{self.COLOR_RESET}")
            
            while self.running:
                conn, addr = tcp_socket.accept()
                print(f"[{self.team_name}] Accepted TCP connection from {addr}")
                threading.Thread(target=self.handle_tcp_connection, args=(conn, addr), daemon=True).start()

    def _udp_listener(self):
        """UDP listener loop."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Bind to our known UDP port
            udp_socket.bind(('', self.udp_port))
            print(f"{self.COLOR_BLUE}[{self.team_name}] Listening on UDP port {self.udp_port}{self.COLOR_RESET}")
            while self.running:
                self.handle_udp_connection(udp_socket)

    def print_summary(self):
        print(f"{self.COLOR_GREEN}\n--- Server Summary ---{self.COLOR_RESET}")
        print(f"TCP Requests Handled: {self.stats['tcp_requests']}")
        print(f"UDP Requests Handled: {self.stats['udp_requests']}")

    def send_payload(self, udp_socket, client_addr, total_segments, current_segment, payload_data):
        """
        Sends a payload message to the client following the specified format.
        Format:
        - Magic cookie (4 bytes): 0xabcddcba
        - Message type (1 byte): 0x4
        - Total segment count (8 bytes)
        - Current segment count (8 bytes)
        - Actual payload (remaining bytes)
        """
        magic_cookie = self.MAGIC_COOKIE
        message_type = 0x4
        total_segments_bytes = struct.pack('!Q', total_segments)
        current_segment_bytes = struct.pack('!Q', current_segment)
        payload = (
            struct.pack('!IB', magic_cookie, message_type)
            + total_segments_bytes
            + current_segment_bytes
            + payload_data
        )
        udp_socket.sendto(payload, client_addr)
        print(
            f"{self.COLOR_GREEN}[{self.team_name}] Sent payload segment {current_segment}/{total_segments}{self.COLOR_RESET}"
        )
