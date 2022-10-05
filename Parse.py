import Channel
import Client
import string

class Parse:

    def __init__(self):
        self.client_list = [ ]  # Holds a list of the Client class objects
        self.channel_list = [ ]  # Holds a list of the Channel class objects
        self.hostname = None

    def update_clients(self, connection, address):
        self.client_list.append(Client.Client(connection,address))
        self.client_list[0].set_hostname(self.hostname)

    def add_hostname(self, hostname):
        self.hostname = hostname

    # Method used to search which of the IRC commands is being invoked
    def search_commands(self, client_connection, command, line):

        # For clients in the client list check if their connection is the same as the socket in the write list
        for c in self.client_list:
            if c.connection is client_connection:
                client = c     

        if "NICK" in command:
            self.nick(client, command[1])
            return True
        elif "USER" in command:
            self.user(client, command[1], command[4])
            return True
        elif "/join" in command or "JOIN" in command:
            self.join(client, command[1])
            return True
        elif "PRIVMSG" in command:
            self.privmsg(client, command[1], line)
            return True
        elif "MODE" in command:
            mode = ":" + client.hostname + " 324 " + client.nickname + command[1] + " +\n"
            client.connection.send( bytes(mode, 'utf-8') )
            return True
        elif "WHO" in command:
            print(command)
            self.who(client, command[1])
            return True
        elif "PART" in command:
            self.part(client, command[1])
        elif "QUIT" in command:
            self.quit(client)
        else:
            return False


    # Function used to create the 2 types of prefixes for the server commands
    def create_prefix(self, client, code, type, operands):
        # If there is no code entered or no operands then set them to be a blank string
        if code == None:
            code = ""
        if operands == None:
            operands = ""

        # Checks which type of prefix is required
        if type == 1:
            prefix = ":" + client.hostname + " " + code + " " + client.nickname + " " + operands + " " 
        else:
            prefix = ":" + client.nickname + "!" + client.real_name + "@" + client.address[0] + " " + operands + " "

        # Returns the prefix that was created
        return prefix


    # Function used to create the welcome message for a user joining the IRC Server
    def welcome_message(self, client):
        welcome = self.create_prefix(client, "001", 1, None) + "Welcome to our IRC server\n"
        host = self.create_prefix(client, "002", 1, None) + "Your host is: " + client.hostname + "\n"
        creation_time = self.create_prefix(client, "003", 1, None) + "This server was created some time\n"
        server_name = self.create_prefix(client, "004", 1, None) + "Group 8 IRC server\n"

        client.connection.send(bytes(welcome, 'utf-8') )
        client.connection.send(bytes(host,'utf-8') )
        client.connection.send(bytes(creation_time, 'utf-8') )
        client.connection.send(bytes(server_name, 'utf-8') )


    # Method used to check if a nickname given by a client is valid
    def nick(self, client, operand):
        RPL = ":" + self.hostname + " 433 " + client.server_name + " " + operand # Reply used to tell the client the nickname was not valid

        if client.hostname is None:
            client.set_hostname(self.hostname)

        #if the clients nickname is already set to the operand then exit function
        if client.nickname == operand:
            return True

        # for the nicknames of all the clients in the client list, check if the entered operand has already been taken
        for n in self.client_list:
            if n.nickname == operand:
                print("Nickname already taken")
                RPL = RPL + "Nickname is already in use\n"
                client.connection.send( bytes(RPL, 'utf-8') )       
                return False

        if operand[0].isnumeric():
            print("Name cannot start with a number")
            RPL = RPL + "Name cannot start with a number\n"
            client.connection.send( bytes(RPL, 'utf-8') )    
            return False

        # Checks if the entered operand is blank
        if operand == "":
            print("\nName cannot be blank")
            RPL = RPL + "Name cannot be blank\n"
            client.connection.send( bytes(RPL, 'utf-8') )    
            return False

        elif len(operand) > 9:
            print("Nickname is too long")
            RPL = RPL + "Name is too long\n"
            client.connection.send( bytes(RPL, 'utf-8') )

        # If the realname has already been set then the USER command has already been run and the nickname can be set and complete the login process to the IRC Server
        elif client.real_name is not None:
            client.set_nickname(operand)
            self.welcome_message(client)
            return True

        # Set the users nickname to the entered operand
        else:
            print("nickname has been set to: " + operand)
            client.set_nickname(operand)
            return True


    # Method used to run the USER command
    def user(self, client, operand1, operand2):
        if client.hostname is None:
            client.set_hostname(self.hostname)

        # Checks if the operand for the real name starts with a colon
        if operand2[0] == ":":
            client.set_real_name(operand2)

        # Calls the nick command to check if the entered nickname is valid
        if self.nick(client, operand1):
            client.set_hostname(self.hostname)
            print("\n", client.nickname, " : ", client.hostname, " : ", client.server_name, " : ", client.real_name, "\n")
            self.welcome_message(client)


    # function used to run the /join command
    def join(self, client, name):
        # Creates the default messages for joining a channel
        join_message = self.create_prefix(client, None, 2, "JOIN " + name) + "\n"
        topic_message = self.create_prefix(client, "331", 1, name) + "No topic set\n"
        end_list = self.create_prefix(client, "366", 1, name) + "End of NAMES list\n"

        #Boolean variable used to store if the channel was found
        not_found = True

        # if the channel name is viable
        if name[0] == '#':
            # search for all the objects of channel in the channel list
            for channel in self.channel_list:
                # if the channel name already exists then the client is added to the list of clients on the channel                
                if channel.channel_name == name:
                    message = self.create_prefix(client, None, 2, "PRIVMSG " + name) + "User " + client.nickname + " Has connected to " + name + "\n"
                    channel.channel_message(client, message)
                    channel.add_client(client)
                    add_name = channel.rpl_name(client) + "\n"
                    not_found = False
                
            # if the channel does not exist and will be made and added to the channel list
            if not_found:
                add_name = self.create_prefix(client, "353", 1, "= " + name) + client.nickname
                self.channel_list.append(Channel.Channel(name, client, add_name))
                add_name = add_name + "\n"

            print(join_message)

            #send the joining channel messages to the client
            client.connection.send( bytes(join_message, 'utf-8') )
            client.connection.send( bytes(topic_message, 'utf-8') )
            client.connection.send( bytes(add_name, 'utf-8') )
            client.connection.send( bytes(end_list, 'utf-8') )

            # add the channels name that the user is currently in 
            client.set_channel(name)

        else:
            client.connection.send("Channel names must start with a #\n".encode('utf-8'))
            return False


    # Function used to allow one user to send a message directly to another
    def privmsg(self, client, name, msg):
        if name is not None and msg is not None:  # checks the command is not missing any parameters
            msg = msg.replace("PRIVMSG " + name + " ", '')
            msg = msg.replace(" :", '')

            message = self.create_prefix(client, None, 2, "PRIVMSG " + name) + msg + "\n"

            for n in self.client_list:  # loop through all the clients in the client list

                # check to see if client has a matching nickname 
                if n.nickname == name:  
                    n.connection.send( bytes(message, 'utf-8') )
                    break

                #else if the clients current channel matches the entered name then send a channel message from the client to the channel they are in
                elif n.current_channel == name:
                    for channel in self.channel_list:
                        if channel.channel_name == client.current_channel:
                            channel.channel_message(client, message)
                    break
                    
                else:
                    client.connection.send("No one found with that nickname or channel by that name\n".encode())
        else:
            client.connection.send("Incorrect command format for PRIVMSG (name) (message)\n".encode())


    # Function used to answer the clients who command to check to is connected 
    def who(self, client, msg):
            # Checks if the who is directed at a channel and prints the relevant message for the correct channel the client is in
            if "#" in msg:
                print("Channel who detected \n")
                for channel in self.channel_list:
                    print(channel.channel_name + " : " + msg)
                    if channel.channel_name == msg:
                        print("Channel found \n")
                        for conn in channel.connected_clients:
                            print("Connection found: " + conn.nickname)
                            RPL = self.create_prefix(client, "352", 1, msg + " " + client.nickname + " " +client.address[0] + " " + self.hostname + " " + conn.nickname + " H") + "0 " + conn.real_name + "\n"
                            client.connection.send( bytes(RPL, 'utf-8') ) 

                    # Creates the end of who reply message
                    RPL = self.create_prefix(client, "315", 1, msg) + "End of WHO list\n"
                    client.connection.send( bytes(RPL, 'utf-8') )

            # else it must be a client who
            else:
                # Loops through all connected clients to check if their nickname matches the entered name
                for c in self.client_list:
                    if c.nickname is msg:
                        RPL = self.create_prefix(client, "352", 1, msg + " " + client.nickname + " " + client.address[0] + " " + self.hostname + " " + c.nickname + " H") + "0 " + c.real_name + "\n"
                        client.connection.send( bytes(RPL, 'utf-8') )
                        RPL = self.create_prefix(client, "315", 1, msg) + "End of WHO list\n"
                        client.connection.send( bytes(RPL, 'utf-8') )


    # Part function used to disconnect the client from a server 
    def part(self, client, operand):

        # Checks if the operand was a channel name
        if "#" in operand:
            # Creates a reply message for leaving the channel
            RPL = self.create_prefix(client, None, 2, "PART " + operand) + "Leaving\n"

            # Creates a message to tell the users of the channel that the client has disconnected
            message = self.create_prefix(client, None, 2, "PRIVMSG " + operand) + "User " + client.nickname + " Has parted from " + operand + "\n"

            # Loops through all channels in the channel list to find if the client is within the channel specified
            for channel in self.channel_list:
                if channel.channel_name == operand and client.current_channel == operand:
                    channel.channel_message(client, message)
                    client.current_channel == None
                    channel.remove_RPL_name(client)

                # Loops through all clients connected to the channel to check for the connection of the leaving client
                for clients in channel.connected_clients:
                    if clients.connection == client.connection:
                        channel.connected_clients.remove(clients)

            client.connection.send( bytes(RPL, 'utf-8') ) # Sends the message telling all users the client has disconnected
        else:
            client.connection.send( "Invalid operand\n".encode )


    #Quit function used to disconnect client after a QUIT command
    def quit(self, client):
        if client.current_channel is not None:
            self.part(client, client.current_channel)

        self.client_list.remove(client) # Removes the client from the client list

        return client.connection