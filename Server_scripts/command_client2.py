import socket


def client(message, ip='localhost', port=50326):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(4096)
        print "Received: %s" % str(response)
    finally:
        sock.close()
    return response

while True:
    msg = raw_input()
    data = client(msg)
    print data