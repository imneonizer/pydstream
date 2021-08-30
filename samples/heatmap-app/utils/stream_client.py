import zmq
import numpy as np
from serialize import SerializingContext
import cv2

class StreamReceiver:
    def __init__(self, host="0.0.0.0", zmq_port=5555):
        self.context = SerializingContext()
        self.socket = self.context.socket(zmq.SUB)
        self.host = host
        self.zmq_port = zmq_port
        self.socket.connect('tcp://{}:{}'.format(self.host, self.zmq_port))
        self.socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

    def receive(self):
        msg, image = self.socket.recv_array(copy=False)
        return msg, image

sr = StreamReceiver(zmq_port=5544)

while True:
    msg, image = sr.receive()
    cv2.imshow(msg, image)
    if cv2.waitKey(1) == ord('q'):
        break