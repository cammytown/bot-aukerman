import sys
import subprocess
import zmq
from bot_aukerman.server import Server

# If --server-only flag is set, run server only
#@REVISIT maybe do inverse
if "--server-only" in sys.argv:
    print("Running server")
    server = Server()
    server.start()

else:
    print("Running client")

    # Run this script as a subprocess with --server-only flag
    server = subprocess.Popen([sys.executable, __file__, "--server-only"])

    # Run a basic client
    try:
        print("Connecting to server")
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        user_input = None
        while user_input != 'q':
            user_input = input("Enter something: ")

            if user_input == '1':
                # Generate dialogue for character 1
                request = {
                        "type": "request_dialogue",
                        "character_idx": 0
                        }

            elif user_input == '2':
                # Generate dialogue for character 2
                request = {
                        "type": "request_dialogue",
                        "character_idx": 1
                        }

            else:
                request = {
                        "type": "observe_user_input",
                        "user_input": user_input
                        }

            print("Sending request %s …" % request)
            socket.send_json(request)

            #  Get the reply
            message = socket.recv_json()
            print("Received reply %s [ %s ]" % (request, message))

    except KeyboardInterrupt:
        print("Keyboard interrupted")
        server.terminate()

    except Exception as e:
        server.terminate()
        raise e
