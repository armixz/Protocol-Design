import Services

import os
import socket
import threading

# Static IP and Port of SERVER
SRVR_ADDR = ('10.0.0.1', 59001)

# Static IP and Port of RENDERER for CONTROLLER communcation
C_REND_ADDR = ('10.0.0.2', 59002)
S_REND_ADDR = ('10.0.0.2', 59003)

# Maximum Message Size
MSG_SIZE = 500

def start():
    """Starts main renderer process."""

    # Creates sockets used for communication with SERVER and CONTROLLER
    c_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    c_sock.bind(C_REND_ADDR)
    s_sock.bind(S_REND_ADDR)

    # Main control loop
    while(True):

        # Waits for message from CONTROLLER
        data, address = c_sock.recvfrom(MSG_SIZE)
        messageType, morePortions, message = Services.parseMessage(data)
        
        if messageType =='20':     # Request file to render
            # Sends 'request file' message to SERVER
            message = Services.build_Message(messageType, morePortions, message)
            s_sock.sendto(message, SRVR_ADDR)

            # Creates child process to render file contents from SERVER
            global p
            p = threading.Thread(target=renderFile, args=(c_sock,s_sock, address))
            p.start()
            
            # Sends response to CONTROLLER that rendering has begun
            message = Services.build_Message('22', '0', '')
            c_sock.sendto(message, address)

        elif messageType =='30':     # pause request
            # Sends 'pause request' to SERVER
            message = Services.build_Message(messageType, morePortions, message)
            s_sock.sendto(message, (SRVR_ADDR))

        elif messageType =='32':     # Resume request
            # Sends 'resume request' to SERVER
            message = Services.build_Message(messageType, morePortions, message)
            s_sock.sendto(message, (SRVR_ADDR))

        elif messageType == '34':    # Restart request
            # Sends 'restart request' to SERVER
            message = Services.build_Message(messageType, morePortions, message)
            s_sock.sendto(message, (SRVR_ADDR))

        elif messageType =='99':    # EXIT Command
            s_sock.close()
            c_sock.close()
            os._exit(0)

def renderFile(c_sock, s_sock, c_address):
    """
    Begins rendering requested file.

        Receives files content messages from SERVER and
        prints the contents to the screen.

    args:
        c_sock : socket obj used to send messages to CONTROLLER
        s_sock : socket obj used to receive message from SERVER
        c_address : (str, int) tuple containing IP/PORT of CONTROLLER
    """
    rendering = True
    # Continues rendering until final rendering message is received from SERVER
    while(rendering):
        # Waits for message from SERVER
        data, _ = s_sock.recvfrom(MSG_SIZE)
        messageType, morePortions, message = Services.parseMessage(data)
        
        if messageType ==  '21' : # File contents message
            print(message, end='', flush=True) # Prints file contents

            # Checks if there are more portions of the file
            if(morePortions == '0'):
                # Sends message to CONTROLLER to indicate rendering has finished
                message = Services.build_Message('23', '0', '')
                c_sock.sendto(message,c_address)
                rendering = False
        elif messageType == '31' :  # Pause response
            print("\nRendering Paused")
        elif messageType == '33' :  # Resume response
            print("\nRendering Resumed")
        elif messageType == '35' :  # Restart response
            print("\nRendering Restarted")
        print()

if __name__ == '__main__':
    start()