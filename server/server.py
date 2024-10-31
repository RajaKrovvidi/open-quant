import asyncio
import tornado.web
import tornado.gen
import tornado.httpserver
import os
import json
import numpy as np
import msgpack
import datetime

from task_manager import TaskManager
from payload_parser import PayloadParser
from persist_queue_manager import PersistQueueManager


class AuthAnalyticsApp(tornado.web.RequestHandler):


    def prepare(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("charset", "UTF-8")

    def post(self):

        print('received....' + str(self.request.body))
        self.write({"access_token": "allowed"})

class AnalyticsApp(tornado.web.RequestHandler):


    def prepare(self):
        self.set_header("Content-Type", 'application/x-msgpack')
        self.set_header("charset", "UTF-8")

    def get(self):
        print('get...')
        self.write({"test": "get-pass"})

    def post(self):

        #print('received....' + str(self.request.body))
        body = msgpack.loads(self.request.body)
        print('post....' + str(body))

        parsed_data = PayloadParser.parse_payload(body)
        print('parsed data is ' + str(parsed_data))
        results = task_manager.process_payload(parsed_data)
        print('Got results ' + str(results))
        # per measure
        # per position
        # per date
        # measure
        """
        vals = {
            '$type': 'Risk',
            'val': 0.01,
        }

        #results = [[[[vals]]*3]*4]
        results = [[[[{'$type': 'Risk', 'val': 150391.16254638787}], [{'$type': 'Risk', 'val': 201101.7375688183}], [{'$type': 'Risk', 'val': -192367.76098476048}]],
                    [[{'$type': 'Risk', 'val': 2229.785210993403}], [{'$type': 'Risk', 'val': 2155.328947221249}], [{'$type': 'Risk', 'val': 13.186445090919733}]],
                    [[{'$type': 'Risk', 'val': 18.170200030639535}], [{'$type': 'Risk', 'val': 12.030347647785675}], [{'$type': 'Risk', 'val': -0.0019750328501686454}]],
                    [[{'$type': 'Risk', 'val': 441262.70378871914}], [{'$type': 'Risk', 'val': 588632.2426292432}], [{'$type': 'Risk', 'val': np.nan }]]]]

        #{  'Vega' : [ [1.0, 2.0, 3.0, 0.0], [1.5, 2.5, 3.5, 0.0] , [3.1, 3.2, 3.3, 3.4]] }
        print(results)
        """
        print('sending results ')
        self.write(msgpack.dumps(results))

def make_app():
    print ("Making Open Quant Server App for Tornado")
    return tornado.web.Application(
        [
            (r"//v1/risk/calculate/bulk", AnalyticsApp),
            (r"/auth", AuthAnalyticsApp),
            (r"/", AnalyticsApp),

        ]
   )

async def main():
    request_queue_path = 'OpenQuantAPI_Server_v1.0_request'
    response_queue_path = 'OpenQuantAPI_Server_v1.0_response'
    global task_manager
    task_manager = TaskManager(PersistQueueManager(request_queue_path),  PersistQueueManager(response_queue_path))

    app = make_app()
    ssl_options = {
        "certfile": os.path.join(r"C:\Users\Surfer" , "cert.pem" ),
        "keyfile":  os.path.join(r"C:\Users\Surfer", "key.pem")
    }
    http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
    print( 'Launching analytics server ...')
    http_server.listen(8888)
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())