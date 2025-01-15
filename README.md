# File Transfer Server and Client

This project demonstrates a simple file transfer system using a server and client architecture. The server broadcasts its availability over UDP, and the client listens for these broadcasts, then establishes TCP and/or UDP connections to request and download files.

## Features

- **Server**:
  - Broadcasts availability via UDP.
  - Handles multiple clients for file requests over TCP and UDP.
  - Simulates file transfers by sending dummy data.
  - Tracks and displays server statistics (number of TCP/UDP requests).

- **Client**:
  - Listens for server offers via UDP.
  - Establishes TCP and/or UDP connections to download files.
  - Measures and displays file transfer statistics (speed, packet success rate, etc.).

## Requirements

- Python 3.6 or newer
- Socket library (part of Python standard library)
- Threading library (part of Python standard library)

## Usage

### 1. Server Setup

Run the server on the desired host machine:

```python
from server import Server

# Parameters
team_name = "TeamServer"
ip_address = "0.0.0.0"  # Listen on all interfaces
udp_port = 13117         # UDP port for broadcasting
tcp_port = 6000          # TCP port for file transfer

# Start server
server = Server(team_name, ip_address, udp_port, tcp_port)
server.start()
```

### 2. Client Setup

Run the client on the same or a different machine:

```python
from client import Client

# Parameters
team_name = "TeamClient"
requested_file_size = 1000000  # 1 MB
tcp_connections = 1           # Number of TCP connections to establish
udp_connections = 1           # Number of UDP connections to establish
broadcast_port = 13117        # Must match the server's UDP port

# Start client
client = Client(team_name, requested_file_size, tcp_connections, udp_connections, broadcast_port)
client.start()
```

### 3. Running the System

- Start the **server** first to begin broadcasting its availability.
- Start the **client** to listen for broadcasts and initiate file transfers.

## Configuration

- The `udp_port` in the server and the `broadcast_port` in the client must match.
- To run the server and client on the **same machine**, use `ip_address = "127.0.0.1"` in the server.
- To run on **different machines** in the same LAN:
  - Use `ip_address = "0.0.0.0"` in the server.
  - Ensure the client and server are on the same subnet.
  - Make sure the firewall allows UDP and TCP traffic on the specified ports.

## Example Output

### Server

```
[TeamServer] Server started, listening on IP address 0.0.0.0
[TeamServer] Sending offer broadcast from 192.168.1.10
[TeamServer] Listening on TCP port 6000
[TeamServer] Listening on UDP port 13117
[TeamServer] Handled TCP request from ('192.168.1.11', 50000)
[TeamServer] Handled UDP request from ('192.168.1.11', 50001)
--- Server Summary ---
TCP Requests Handled: 1
UDP Requests Handled: 1
```

### Client

```
[TeamClient] Client started, listening for offer requests...
[TeamClient] Received offer from 192.168.1.10
[TeamClient] TCP transfer #1 finished:
  Total time: 0.25s
  Speed: 32.00 Mbps
[TeamClient] UDP transfer #1 finished:
  Total time: 0.30s
  Speed: 30.00 Mbps
  Packet success: 100%

--- Transfer Summary ---
TCP Transfers:
  Connection #1: Time 0.25s, Speed 32.00 Mbps
UDP Transfers:
  Connection #1: Time 0.30s, Speed 30.00 Mbps, Packet Success 100%
```

## Notes

- The project uses dummy data (`b'X'`) to simulate file transfers.
- UDP connections calculate packet success rates based on received sequences.
- Adjust `requested_file_size` to test transfers of different sizes.

## License

This project is released under the MIT License.

