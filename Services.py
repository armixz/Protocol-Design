def parseMessage(message):
    message = message.decode()
    yy = message[0:2]       #Message type
    q = message[2]          #Portion flag
    
    payload = ""            #Data/payload
    
    #If message type would have a payload
    '''if(yy == 11 or yy == 20 or yy == 21):
        payload = message[3:]   
    '''
    
    if(len(message) > 3):
        payload = message[3:]

    return yy, q, payload

def build_Message(yy, q, payload):
    message = yy + q + payload 
    return message