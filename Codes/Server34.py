import Services

import multiprocessing as mp
import os
import socket
import time


# Static IP and Port of SERVER
SRVR_ADDR = ('10.0.0.1', 59001)

# Maximum Message Size
MSG_SIZE = 500

   
def start():
    """Starts main server process."""

    # Creates socket used for communication with RENDERER and CONTROLLER
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SRVR_ADDR)

    lastRequestedFile = ''
    exit = False
    pause = mp.Value('i', 0)    # Shared memory unit used for interprocess communication
    # i = 0 NOT paused
    # i = 1 paused

    # Main control loop
    while (not exit):

        # Waits for message from either CONTROLLER or RENDERER
        data, address = sock.recvfrom(MSG_SIZE)
        messageType, morePortions, message = Services.parseMessage(data)
        print('Message Type: ' + messageType)
        print('More Portions: ' + morePortions)
        print('Received Message: ' + message)

        if messageType == '10':     # File list request

            file_list = getFileList()
            portions = portion(file_list) # Portions message in case payload does not if in message
            for p in portions:
                # Sends file list to CONTROLLER
                message = Services.build_Message('11', p[1], p[0])
                sock.sendto(message, address)

        elif messageType == '20':   # Render file request

                lastRequestedFile = message # Stores file name in case a restart is requested
                global proc # Child thread is created to send file contents to RENDERER
                proc = mp.Process(target=renderFile, args=(message, pause, address))
                proc.start()

        elif messageType == '30':   # Pause File request
            pause.value = 1  # Shared mem is updated to indicate pausing
            message = Services.build_Message('31','0','')
            sock.sendto(message,address)

        elif messageType == '32':          #Resume File
            pause.value = 0 # Shared mem is updated to indicate unpausing
            message = Services.build_Message('33','0','')
            sock.sendto(message,address)

        elif messageType ==  '34':          #Restart File
            proc.terminate()    # Currently rendering process is terminated
            pause.value = 0     # Shared mem value is reset

            # Restarts response sent to RENDERER
            message = Services.build_Message('35','0','')
            sock.sendto(message,address)

            # New rendering process is created
            proc = mp.Process(target=renderFile, args=(lastRequestedFile, pause, address))
            proc.start()

        elif messageType ==  '99':  # Exit Command
            proc.join()
            exit = True


def renderFile(filename, pause, address):
    """
    Begins sending file conent of requested file.

        Opens requested file and portions it into messages
        to be sent to RENDERER. Sends messages if unpaused

    args:
        filename : socket obj used to send messages to CONTROLLER
        pause : multiprocessing Value object used to indicate pause/unpause
        address : (str, int) tuple containing IP/PORT of RENDERER
    """
    # Creates new socket to communicate with RENDERER
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    f = open('./files/' + filename, "r") # Opens requested file

    # Reads entire file into memory
    fileContents = f.read()

    portions = portion(fileContents)    # Portions message in case payload does not if in message
    for p in portions:
        # Delays the time between messages to allow the user to access rendering controls
        time.sleep(.5)
        while(pause.value == 1):        # Pause is enabled, will NOT send messages to RENDERER
            pass
        if(pause.value == 0):           # Pause is disabled, will begin sending messages to RENDER
            # Sends file contents to RENDERER
            message = Services.build_Message('21', p[1], p[0])
            sock.sendto(message, address)

def getFileList():
    """
    Retrieves file names of all files residing in '/files'

    returns:
        list : lsts of file names
    """
    file_list = ','
    for _, _, file in os.walk('./files'):
        file_list = file_list.join(file)
    return file_list

def portion(message):
    """
    Portions message into portions of at most length MSG_SIZE

    args:
        message (str) : payload of message to be portioned
    returns:
        list : list containing a list file content and a corresponding Q value
    """

    messageLen = len(message.encode())
    portionedMessage = []

    for i in range(0, messageLen, MSG_SIZE-3):
        portionedMessage.append([message[i:i+MSG_SIZE-3],'1'])

    portionedMessage[len(portionedMessage)-1][1] = '0'  # Indicates last portion

    return portionedMessage

if __name__ == '__main__':
    start()