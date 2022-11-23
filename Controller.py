import socket
import Services

#print(file_list.split(','))

SRVR_IP = "127.0.0.1"
CNTRL_PORT = 9002
SRVR_PORT = 59002
MSG_SIZE = 1000

def main():
    data = ['MESSAGE']*1025
    s_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = ''.join(data)
    s_sock.sendto(Services.build_Message('10','0',"TESTING").encode(), (SRVR_IP, SRVR_PORT))
    data, address = s_sock.recvfrom(1000)
    print(data)

if __name__ == "__main__":
    main()