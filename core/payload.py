import threading

class Payload(object):
    PAYLOAD_ID = 0
    PAYLOAD_ID_LOCK = threading.Lock()

    def __init__(self, data=""):
        self.data = data
        with Payload.PAYLOAD_ID_LOCK:
            self.id = Payload.PAYLOAD_ID
            Payload.PAYLOAD_ID += 1
