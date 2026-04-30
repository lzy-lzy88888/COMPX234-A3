import socket
import sys
import os

def receive_n(sock, num_bytes):
    data = b""
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            raise RuntimeError("Connection closed")
        data += chunk
    return data
def main():
    if len(sys.argv) != 4:
        print("Usage: python tuple_space_client.py <server-hostname> <server-port> <input-file>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    if not (50000 <= port <= 59999):
        print("Error: port must be between 50000 and 59999")
        sys.exit(1)
    input_file_path = sys.argv[3]

    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' does not exist.")
        sys.exit(1)

    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # TASK 1: Create a TCP/IP socket and connect it to the server.
    # Hint: socket.socket(socket.AF_INET, socket.SOCK_STREAM) creates the socket.
    # Then call sock.connect((hostname, port)) to connect.
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname,port))


    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(" ", 2)
            cmd = parts[0]
            message = ""

            
            # TASK 2: Build the protocol message string to send to the server.
            # Format:  "NNN X key"        for READ / GET
            #          "NNN P key value"   for PUT
            # where NNN is the total message length as a zero-padded 3-digit number,
            # X is "R" for READ and "G" for GET.
            # Hint: for READ/GET, size = 6 + len(key). For PUT, size = 7 + len(key) + len(value).
            # Reject lines with invalid format or key+" "+value > 970 chars.
            if cmd == "READ":
                if len(parts) < 2:
                    print(f"{line}: ERR Invalid command")
                    continue
                key = parts[1]
                msg = f" R {key}"
                total_len= len(msg) + 6
                if total_len > 999 :
                    print(f"{line}: ERR Message too long")
                    continue
                message = f"{total_len:03d} R {msg}"

            elif cmd == "GET":
                if len(parts) < 2:
                    print(f"{line}: ERR Invalid command")
                    continue
                key = parts[1]
                msg = f" G {key}"
                total_len = len(msg) + 6
                if total_len > 999 :
                    print(f"{line}: ERR Message too long")
                    continue
                message = f"{total_len:03d} G {msg}"

            elif cmd == "PUT":
                if len(parts) < 3:
                    print(f"{line}: ERR Invalid command")
                    continue
                key = parts[1]
                value = parts[2]
                msg = f" P {key} {value}"
                total_len = len(msg)
                if total_len> 999 or len(f"{key} {value}") > 970:
                    print(f"{line}: ERR Message too long")
                    continue
                message = f"{total_len:03d} P {msg}"
            else:
                print(f"{line}: ERR Unknown command")
                continue

            

            # TASK 3: Send the message to the server, then receive the response.
            # - Send:    sock.sendall(message.encode())
            # - Receive: first read 3 bytes to get the response size (like the server does).
            #            Then read the remaining (size - 3) bytes to get the response body.
            sock.sendall(message.encode())
            Response=sock.recv(3)
            response_size = int(Response.decode())
            response_buffer = receive_n(sock, response_size - 3)

            response = response_buffer.decode().strip()
            print(f"{line}: {response}")

    except (socket.error, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # TASK 4: Close the socket when done (already called for you — explain why
        #Close the socket can release the port resources
        # finally: is the right place to do this even if an error occurs above).
        sock.close()

if __name__ == "__main__":
    main()