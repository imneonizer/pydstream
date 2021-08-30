import zmq
import numpy as np
from .serialize import SerializingContext


class StreamServer:
    def __init__(self, host="0.0.0.0", zmq_port=5555):
        self.context = SerializingContext()
        self.socket = self.context.socket(zmq.PUB)

        # limit publisher buffer size
        self.socket.setsockopt(zmq.SNDHWM, 2)

        self.host = host
        self.zmq_port = zmq_port
        self.socket.bind('tcp://{}:{}'.format(self.host, self.zmq_port))

    def send(self, frame, idx=0):
        try:
            self.socket.send_array(
                (frame if frame.flags['C_CONTIGUOUS']
                 else np.ascontiguousarray(frame)),
                str(idx), copy=False)
        except Exception as e:
            print(e)
