import Server
import socket

# main function
if __name__ == '__main__':
    IRC_server = Server.Server()

    # Try to create the socket and begin the select statement loop
    try:
        IRC_server.create_socket()
        IRC_server.selecting()

    # Catches general socket errors
    except socket.error as e:
        print("Error: ", e)

    #   Catches errors with connecting clients
    except socket.gaierror as e:
        print("Error: ", e)

    #Finally exits the program
    finally:
        print("Closing IRC server")
        IRC_server.server_socket.shutdown(2)
        IRC_server.server_socket.close()