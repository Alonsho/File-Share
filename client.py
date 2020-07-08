import socket, os, sys, thread

dest_ip = (sys.argv[1])
dest_port = int(sys.argv[2])
filesPath = os.path.dirname(os.path.realpath(__file__))


# sends to server all files in scripts directory and listens for clients who want one of my files
def upload_listener():
    # prepare a string of all the files in the current folder
    script_name = os.path.basename(__file__)
    files = [f for f in os.listdir(filesPath) if os.path.isfile(os.path.join(filesPath, f))]
    files.remove(script_name)
    filesString = (", ".join(files))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # try to connect to the server
    try:
        s.connect((dest_ip, dest_port))
    except socket.error:
        print 'Bad arguments were given for listening client socket'
        exit(1)
    # send the server a message with my listening port and all the files in my current directory
    msg = "1 " + (sys.argv[3]) + " " + filesString + '\n'
    s.send(msg)
    # close the socket
    s.close()
    # open a new socket for listening to clients who want my files
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = '0.0.0.0'
    server_port = int(sys.argv[3])
    try:
        s.bind((server_ip, server_port))
    except OverflowError:
        print 'invalid port given as argument'
        exit(1)
    s.listen(5)
    while True:
        # create a socket for transferring a file to a client who wants it
        client_socket, client_address = s.accept()
        # client will send the name of the file he wants followed by '\n'
        filename = client_socket.recv(1024)
        while not filename[-1] == '\n':
            filename += client_socket.recv(1024)
        filename = filename[:-1]
        fileToSend = ''
        # find the wanted file and open it
        for f in files:
            if filename == f:
                try:
                    file_path = filesPath + '/' + f
                    fileToSend = open(filesPath + '/' + f, 'rb')
                except IOError:
                    print 'error opening the given file, try again'
                break
        # if the file was not found, or there was an error attempting to open it, send a blank message
        if not fileToSend:
            client_socket.send('\n')
            client_socket.close()
            continue
        # send the file in 1024 B packets
        try:
            fileData = fileToSend.read(1024)
            while fileData:
                client_socket.send(fileData)
                fileData = fileToSend.read(1024)
        except IOError:
            print 'error reading the file'
        except socket.error:
            print 'error sending the file'
        # once transfer is done, close file and socket
        fileToSend.close()
        client_socket.close()


# listen to other clients in background
thread.start_new_thread(upload_listener, ())

# download files
while True:
    # enter a search querie
    fileToSearch = raw_input("Search: ")
    # open a socket and connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((dest_ip, dest_port))
    # send the server a search request
    s.send("2 " + fileToSearch + "\n")
    # receive from server all the files that match my search (with the appropriate client socket details)
    filesString = s.recv(1024)
    while not filesString[-1] == '\n':
        filesString += s.recv(1024)
    # close the socket
    s.close()
    # print all the matching files to the user screen
    filesString = filesString[:-1]
    singleFiles = filesString.split(", ")
    if singleFiles[0] == '':
        del singleFiles[0]
    i = 1
    for f in singleFiles:
        userDetails = f.split(" ")
        # do not display to me my files
        if int(userDetails[2] == sys.argv[3]):
            continue
        fileName = f.split(" ")[0]
        print str(i) + " " + fileName
        i += 1
    # check if any matching files were found
    if i == 1:
        print 'No files matching search query were found'
        continue
    # user will choose which file to download
    num = raw_input("Choose: ")
    # check that user inputted a number valid for the given file list
    if not num.isdigit():
        continue
    if int(num) - 1 >= len(singleFiles) or len(singleFiles) == 0 or int(num) == 0:
        continue
    # get the details of the socket associated with the file the user chose
    chosenFile = singleFiles[int(num) - 1]
    userDetails = chosenFile.split(" ")
    ip = userDetails[1]
    port = int(userDetails[2])
    # connect to that socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
    except socket.error:
        print 'error connecting to peer'
        s.close()
        continue
    # open a new file to copy the data to
    try:
        fileToReceive = open(filesPath + '/' + userDetails[0], 'wb')
    except IOError:
        print 'error opening a new file to write to'
        s.close()
        continue
    # send the peer the name of the wanted file
    try:
        s.send(userDetails[0] + '\n')
    except socket.error:
        print 'error sending to peer the wanted file name'
        s.close()
        continue
    # receive the file data from peer and write it to the new file
    try:
        data = s.recv(1024)
        while data:
            fileToReceive.write(data)
            data = s.recv(1024)
    except IOError:
        print 'error writing the received data to file'
    except socket.error:
        print 'error receiving data from peer'
    fileToReceive.close()
    s.close()


