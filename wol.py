import sys
import socket
import subprocess
import argparse

# List the username allowed to Wake on Lan in your domain specifying the name of the pc to wake up and its mac address 
# Usernames are case sensitive! If it doesn t work check the Windows Security Log
# Make sure the Active directory machine can communicate with the PCs and also remember to allow Wake on lan on every PCs
username_pc_dict = {
    "username_1": ["PC_name_1", "00:1A:4B:8C:00:12"],
    "username_2": ["PC_name_2", "00:1A:4B:8C:00:12"],
    "username_3": ["PC_name_3", "00:1A:4B:8C:00:12"]
}

def send_magic_packet(mac_address, ip_address):
    mac_bytes = bytearray.fromhex(mac_address.replace(":", ""))
    magic_packet = b"\xff" * 6 + mac_bytes * 16
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    port = 9 # You can change the port, i used the default one
    # Remember to create a firewall/antivirus rule for the port you want to receive the magic packets
    # The rule should only allow traffic from the ip of the Active Directory Machine (or from the domain)
    sock.sendto(magic_packet, (ip_address, port))
    sock.close()


# Parse username given as argument from the Windows Task Scheduler
parser = argparse.ArgumentParser()
parser.add_argument('--TargetUserName', help='the target user from event 4624')
args = parser.parse_args()

if args.TargetUserName:
    try:
        # Get the username from the command-line argument
        username_event = args.TargetUserName
        username = username_event.lower()

        user_pc_mac = username_pc_dict.get(username)

        pc_name = user_pc_mac[0]
        pc_mac = user_pc_mac[1]
    except:
        print("User not in list")
        sys.exit(1)

    # Get the IP address of the PC using the hostname
    try:
        ip_address = socket.gethostbyname(pc_name)
    except socket.gaierror:
        print(f"Error: Could not resolve hostname {pc_name}")
        sys.exit(1)

    # Send the magic packet to wake up the specified PC
    try:
        send_magic_packet(pc_mac, ip_address)
        print(f"Magic packet sent to {pc_name} ({ip_address})")
    except subprocess.CalledProcessError as e:
        print(f"Error: Could not send magic packet to {pc_name} ({ip_address}): {e}")
        sys.exit(1)
else:
    print("No target user specified.")

sys.exit(0)


