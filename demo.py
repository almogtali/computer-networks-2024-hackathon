import time
from Server import Server
from Client import Client

def demo_server():
    """
    Demonstrates a rough flow of your 10-step scenario.
    """
    # STEP 1: Team Mystic's server
    mystic_server = Server("ServerTeam", "172.1.0.4")
    mystic_server.start()

    # Give Team Valor a different pair of ports, e.g. 13119/13120
    # valor_server = Server("Team Valor", "172.1.0.88")
    # valor_server.start()
    time.sleep(100)

    mystic_server.running = False

def demo_client():
    instinct_client = Client("Team Instinct", requested_file_size=1024*1024*1,  # 1MB for the demo
                             tcp_connections=1, udp_connections=2)
    instinct_client.start()

    # STEP 4: Teams Rocket, Beitar, Katamon start clients (similarly)
    # rocket_client = Client("Team Rocket", requested_file_size=1024*1024*1,  # 1MB
    #                        tcp_connections=1, udp_connections=1)
    # rocket_client.start()

    # beitar_client = Client("Team Beitar", requested_file_size=1024*1024*1,  # 1MB
    #                        tcp_connections=1, udp_connections=1)
    # beitar_client.start()

    # katamon_client = Client("Team Katamon", requested_file_size=1024*1024*1,  # 1MB
    #                         tcp_connections=1, udp_connections=1)
    # katamon_client.start()
    time.sleep(100)


if __name__ == "__main__":
    # Active Your side; Not both
    demo_server()
    # demo_client()
