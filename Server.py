import socket
import codecs
import select
import queue
import Parse

class Server:

    def __init__(self):
        # Global variables
        self.server_socket = None
        self.hostname = None

        self.input_sockets = [ ] # Creates a list of sockets that the server will recieve data from
        self.output_sockets = [ ] # Creates a list to store sockets that the server will output data to
        self.sending_queue = { } # Creates a list of queues to store the messages that the connections want to send

        self.parse = Parse.Parse()


    # Function used to create a socket for the server
    def create_socket(self):
        self.server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)  # Creates the socket for the server
        self.parse.add_hostname( socket.gethostname() )

        # Binds the socket to a port and listens for incoming connections
        print("Server starting on port 6667 ...\n")
        self.server_socket.bind( ('localhost', 6667) )
        self.server_socket.listen(3)


    # Code for the working of select statement based on code from https://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/select/index.html 
    def selecting(self):
        self.input_sockets = [self.server_socket] 

        while True:
            
            readable, writeable, exceptional = select.select(self.input_sockets, self.output_sockets, self.input_sockets) # Select statement that outputs a list of items that are ready to be read or written from or a list of error

            # For loop to loop through all of the items returned to the list of sockets ready to be read from
            for sock in readable:

                # If statement that checks if the socket to be read from is the server socket
                # In this case that means a client is trying to connect to the socket
                if sock is self.server_socket:
                    incoming_connection, incoming_address = sock.accept() # Accepts the client to the server
                    print("\n\n", incoming_address[0], " : ", incoming_address[1], " has connected\n")
                    incoming_connection.setblocking(0)

                    # Adds the connection to the list of expected sockets to read input from
                    self.input_sockets.append(incoming_connection)

                    # Adds the client to the client list as a new Client object
                    self.parse.update_clients(incoming_connection, incoming_address)

                    # Giving the conection a queue for data we want to send to it
                    self.sending_queue[incoming_connection] = queue.Queue()
                
                # If the socket ready to be read from is not the server then the server is receiving data from a client
                else:
                    # Read in data from the client
                    received_data = sock.recv(1024)  

                    if received_data:
                    
                        # decodes the information received from bytes into a string
                        received_data = codecs.decode(received_data)  

                        # Adds the data from the socket to a list of the data that wishes to be sent out from the server
                        self.sending_queue[sock].put(received_data)

                        # Checks if the current socket that wishes to send data is on the output list and if not adds it
                        if sock not in self.output_sockets:
                            self.output_sockets.append(sock)

                    # If there is no data recieved then we should close the sockets connection
                    else:
                        if sock in self.output_sockets:
                            self.output_sockets.remove(sock)
                        
                        self.input_sockets.remove(sock)
                        sock.close()

            # For loop to loop through all of the items returned to the list of sockets ready to be written to
            for sock in writeable:
                try:
                    # Get the message to be sent by the socket
                    msg = self.sending_queue[sock].get_nowait()

                    if msg[0] == ":":
                        print("Server message detected")
                        continue

                # Catches the error thrown if the queue is empty
                except queue.Empty:
                    self.output_sockets.remove(sock)
    
                else:
                    
                    lines = msg.split('\n')  # Splits the new lines into separate strings

                    # For all the lines read in from the client break them up and search for the commands entered
                    for line in lines:
                        print(" ", line, "\n")
                        temp = line.split()
                        con = self.parse.search_commands(sock, temp, line)

                        if type(con) is socket:
                            if con.connection in self.input_sockets:
                                self.input_sockets.remove(con.connection) # Removes the client from the sockets to be read from list

                            if con.connection in self.output_sockets:
                                self.output_sockets.remove(con.connection) # Removes the clients from the sockets wishing to output list


            # Checks if there is any sockets in the exceptional list and if so closes their connection
            for sock in exceptional:
                self.input_sockets.remove(sock)

                if sock in self.output_sockets:
                    self.output_sockets.remove(sock)

                sock.close()
