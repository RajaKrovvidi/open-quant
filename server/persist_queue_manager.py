import persistqueue
from queue_manager import QueueManager

class PersistQueueManager(QueueManager):

    def __init__(self, queue_path):
        self.queue_path = queue_path
        self.queue = persistqueue.SQLiteQueue(queue_path, auto_commit=True)

    def put(self, *args):
        print ( "Adding to queue " + str(args[0]))
        self.queue.put(args[0])

    def get(self):
        return self.queue.get()

    def name(self):
        return self.queue.path
