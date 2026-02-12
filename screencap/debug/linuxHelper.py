import os
import socket
socketPath = "/run/user/goldentoaste_tester.sock"

try:
    os.unlink(socketPath)
except:
    pass

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.bind(socketPath)
os.chmod(socketPath, 0o600)

sock.listen()

con, _addr = sock.accept()
