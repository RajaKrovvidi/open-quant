import msgpack
from persist_queue_manager import PersistQueueManager

request_queue_path = 'OpeQuantAPI_Server_v1.0_request'
response_queue_path = 'OpeQuantAPI_Server_v1.0_response'
request_queue = PersistQueueManager(request_queue_path)
response_queue = PersistQueueManager(response_queue_path)


def main():
    print('starting... ')
    while True:
        try:
            data = msgpack.loads(request_queue.get())
            print('Got .. ' + str(data) )
        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()