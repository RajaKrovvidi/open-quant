import uuid
import msgpack

class TaskManager:

    def __init__(self, request_queue_manager, response_queue_manager):
        self._request_queue_manager = request_queue_manager
        self._response_queue_manager = response_queue_manager
        self._requests = {}
        print('Initialized Task Manager....using req queue {0} and response queue {1}'.format(request_queue_manager.name(), response_queue_manager.name()))

    def create_task(self, payload):
        key = uuid.uuid4()
        self._request_queue_manager.put(msgpack.dumps({'key': str(key), 'request': payload}))
        self._requests[key] = (payload, None)
        return key

    def process_payload(self, payload):
        # inspect payload
        # split payload based on config
        # add tasks to the right corresponding queue based on analytics service provide - payload
        self.create_task(payload)
        print('Waiting to get results ')
        results = self._response_queue_manager.get()
        return results