# File-Share
python implementation of a simple peer-to-peer file sharing platform.

**Description:** The server maps between all available files and the client that each file belongs to. once client script is activated, all files that are in the same directory as the client script are added to servers mapping and can the be found by other clients. Once a client chooses a file to download, a connection with the file owner is created and th file is tranfered from the file owner to the downloading client. Files are downloaded to the downloaders client script directory.

**Running instructions:** Run server at first. Then simply run 2 or more clients from diferent directories (or machines) and share files with each other.
