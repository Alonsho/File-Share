import socket, sys
# create a listening socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '0.0.0.0'
server_port = int(sys.argv[1])
try:
    server.bind((server_ip, server_port))
except OverflowError:
    print 'bad argument given for server socket'
    exit(1)
server.listen(5)
files = {}
while True:
    # create a socket for new clients
    client_socket, client_address = server.accept()
    # receive data from client (if 1 the listening client, if 2 then downloading client)
    data = client_socket.recv(1024)
    if data[0:2] == '1 ':
        while not data[-1] == '\n':
            data += client_socket.recv(1024)
        data = data[2:-1]
        words = data.split(" ", 1)
        # get the port the client will listen on and all the files he offers
        listenPort = words[0]
        userFiles = words[1].split(", ")
        # add all the files the client offers to the files dictionary with the clients listening socket details
        for singleFile in userFiles:
            files[singleFile] = (client_address[0], listenPort)
        # close the socket once all details were given
        client_socket.close()
    # for downloading client:
    elif data[0:2] == '2 ':
        # get the search queried by the user
        while not data[-1] == '\n':
            data += client_socket.recv(1024)
        data = data[2:-1]
        # if the user entered empty input
        if not data:
            client_socket.send('\n')
            client_socket.close()
            continue
        message = ''
        # send to the client a list of all the files that match together with the appropriate listening clients
        # socket details
        for key in sorted(files.keys()):
            if data in key:
                message += ', ' + key + ' ' + files[key][0] + ' ' + files[key][1]
        message = message[2:]
        message += '\n'
        client_socket.send(message)
        client_socket.close()
