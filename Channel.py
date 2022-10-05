# Class to hold all the information about the servers channels
class Channel:

    # Initialisation function for creating a new channel
    def __init__(self, name, client, add_name):
        self.channel_name = name
        self.connected_clients = [ ]
        self.connected_clients.append(client)
        self.add_name = add_name


    # Sets up the IRC RPL message to tell the client about the other clients within a channel
    def rpl_name(self, client):
        self.add_name = self.add_name + " " + client.nickname
    
        return self.add_name

    def remove_RPL_name(self, client):
        self.add_name = self.add_name.replace(client.nickname, '')

    # Function used to add a client to the channel
    def add_client(self, client):
        self.connected_clients.append(client)

    # Function used to send a message within a specified channel
    def channel_message(self, client, message):
        for c in self.connected_clients:
            if c.connection != client.connection:
                c.connection.send( bytes(message, 'utf-8') )