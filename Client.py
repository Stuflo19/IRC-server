# Class used to hold the details of a connected client
class Client:

    # Initialise with clients socket information
    def __init__(self, connection, address):
        self.connection = connection  # Holds the clients connection
        self.address = address  # Holds the clients address
        self.nickname = None  # Holds the nickname of the client set by the NICK command
        self.hostname = None  # Holds the host name from the USER command
        self.server_name = "*"  # Holds the server_name from the USER command
        self.real_name = None  # Holds the real_name from the USER command
        self.current_channel = None  # Holds the information of the channel that the client is currently connected to (unsure if this is required)

    # Function to set the clients nickname
    def set_nickname(self, nickname):
        self.nickname = nickname

    # Function to set the clients host_name
    def set_hostname(self, hostname):
        self.hostname = hostname

    # Function to set the clients server_name
    def set_server_name(self, server_name):
        self.server_name = server_name

    # Function to set the clients real_name
    def set_real_name(self, real_name):
        self.real_name = real_name
        self.real_name = self.real_name.replace(':', '')

    # Function to set the clients current connected channel
    def set_channel(self, channel):
        self.current_channel = channel