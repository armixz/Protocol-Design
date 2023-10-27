import Services

import multiprocessing as mp
import socket
import threading

mp.allow_connection_pickling()


# Static IP and Port of SERVER and RENDERER
SRVR_ADDR = ('10.0.0.1', 59001)
REND_ADDR = ('10.0.0.2', 59002)

# Maximum Message Size
MSG_SIZE = 500

def start():
    """Starts controller process."""

    # Creates socket used for communication with SERVER and RENDERER
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # File list request
    sock.sendto(Services.build_Message('10','0',''), SRVR_ADDR)

    # Receive file list
    data, _ = sock.recvfrom(MSG_SIZE)
    messageType, _, message = Services.parseMessage(data)
    if messageType == '11':
        files = message.split(',')

    global rendering    # Control variable used by each thread to communicate
    rendering = False
    exit = False

    # Main control loop
    while (not exit):

        # Display files to user
        for i in range(len(files)):
                print('[{0}] {1}'.format(i+1, files[i]))
        print('[{0}] EXIT'.format(len(files) + 1))
        print('Select a file: ')

        x = int(input())

        if (x == (len(files) + 1)):    # User chooses EXIT
            exit = True
            message = Services.build_Message('99', '0', '')
            sock.sendto(message, REND_ADDR)
            sock.sendto(message, SRVR_ADDR)
            sock.close()
            break

        elif (x > len(files)):    # User enters invalid input
            print('Invalid Selection')

        else:    # User chooses valid file
            x = files[x-1]

            # Sends 'request file' message to RENDERER
            message = Services.build_Message('20', '0', x)
            sock.sendto(message, REND_ADDR)

            # Waits for acknowledgement from RENDERER
            data, _ = sock.recvfrom(MSG_SIZE)
            messageType, _, message = Services.parseMessage(data)

            # Display rendering controls to user
            if messageType == '22':

                # Communicates to rendering thread that rendering is happening
                rendering = True
                
                # New thread to display rendering controls
                global p
                p = threading.Thread(target=render_controls, args=(sock,))
                p.start()

        # Waits RENDERER to finish rendering
        while(rendering):
            data, _ = sock.recvfrom(MSG_SIZE)
            messageType, _, message = Services.parseMessage(data)
            if(messageType == '23'):
                # Communicates to rendering thread that rendering is finished
                rendering = False

                print("Rendering Complete Press Enter")
                p.join() # Rendering thread joins main thread to display file list again.

def render_controls(sock):
    """
    Begins displaying render controls to user.

        Gets input from the user, then sends a corresponding
        request request to RENDERER

    args:
        sock : socket obj used to send messages to RENDERER
    """

    # Runs until main thread receives 'rendering finished' message
    while(rendering):

        # Displays options to user
        print("1. Pause \n2. Resume \n3. Restart")
        selection = input()

        if rendering:   # Checks if RENDERER is still rendering

            if selection == '1':    # Users chooses 'Pause'
                # Sends 'pause request' to RENDERER
                message = Services.build_Message('30','0','')
                sock.sendto(message, REND_ADDR)

            elif selection == '2':    # Users chooses 'Resume'
                # Send 'resume request' to RENDERER
                message = Services.build_Message('32','0','')
                sock.sendto(message, REND_ADDR)

            elif selection == '3':    # Users chooses 'Restart'
                # Sends 'restart request' to RENDERER
                message = Services.build_Message('34','0','')
                sock.sendto(message, REND_ADDR)

if __name__ == '__main__':
    start()