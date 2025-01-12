import time
from Server import Server
from Client import Client

def demo_scenario():
    """
    Demonstrates a rough flow of your 10-step scenario.
    """
    # STEP 1: Team Mystic's server
    mystic_server = Server("Team Mystic", "172.1.0.4", 13117, 13118)
    mystic_server.start()

    # Give Team Valor a different pair of ports, e.g. 13119/13120
    valor_server = Server("Team Valor", "172.1.0.88", 13119, 13120)
    valor_server.start()

    # STEP 3: Team Instinct starts client with 1GB, 1 TCP, 2 UDP
    # (1 GB = 1024 * 1024 * 1024, but let's keep it small for the example)
    instinct_client = Client("Team Instinct", requested_file_size=1024*1024*1,  # 1MB for the demo
                             tcp_connections=1, udp_connections=2)
    instinct_client.start()

    # STEP 4: Teams Rocket, Beitar, Katamon start clients (similarly)
    rocket_client = Client("Team Rocket", requested_file_size=1024*1024*1,  # 1MB
                           tcp_connections=1, udp_connections=1)
    rocket_client.start()

    beitar_client = Client("Team Beitar", requested_file_size=1024*1024*1,  # 1MB
                           tcp_connections=1, udp_connections=1)
    beitar_client.start()

    katamon_client = Client("Team Katamon", requested_file_size=1024*1024*1,  # 1MB
                            tcp_connections=1, udp_connections=1)
    katamon_client.start()

    # Let the demo run for ~10 seconds to see console outputs
    # In a real app, you'd have more robust synchronization or signals.
    time.sleep(10)

    # STEP 10: When all transfers are completed, the clients might print "All transfers complete!"
    # For the sake of the example, we just stop the servers:
    mystic_server.running = False
    valor_server.running = False

    print("\nDemo finished. You can see above how servers offered, clients connected, etc.\n")

if __name__ == "__main__":
    demo_scenario()
