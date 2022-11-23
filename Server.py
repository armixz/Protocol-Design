import socket
import os
import Services

SRVR_IP = '127.0.0.1'
REND_PORT = 59001
CTRL_PORT = 59002
MSG_SIZE = 1000


def main():
    # Creating Controller/Renderer Sockets
    c_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    r_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    c_sock.bind((SRVR_IP, CTRL_PORT))
    r_sock.bind((SRVR_IP, REND_PORT))

    exit = False
    while not exit:
        data, address = c_sock.recvfrom(MSG_SIZE)
        messageType, morePortions, data = Services.parseMessage(data)
        print("Message Type: " + messageType)
        print("More Portions: " + morePortions)
        match messageType:
            case '10':
                file_list = getFileList()
                portions = portion(file_list)
                for p in portions:
                    message = Services.build_Message('11',p[1],p[0])
                    c_sock.sendto(message.encode(), address)
            case '20':
                print()
            case '30':
                print()
            case '32':
                print()
            case '34':
                print()
            case '99':
                print()

        print("received message: %s" % data)

def getFileList():
    file_list = ','
    for _, _, file in os.walk("./files"):
        file_list = file_list.join(file)
    print(file_list)
    return file_list

def portion(message):
    messageLen = len(message.encode())
    portionedMessage = []

    for i in range(0, messageLen, MSG_SIZE):
        portionedMessage.append([message[i:i+MSG_SIZE],'1'])

    portionedMessage[len(portionedMessage)-1][1] = '0'

    return portionedMessage
'''
    counter = 0
    if(messageLen > maxSize):
        for i in range(messageLen):
            if((i + maxSize) < messageLen):
                portionedMessage[counter] = message[i:i+maxSize]
            else:
                portionedMessage[counter] = message[i:]
                
            i += maxSize
            counter += 1
    else:
        portionedMessage[0] = message
    
    return portionedMessage
'''
    

if __name__ == '__main__':
    main()