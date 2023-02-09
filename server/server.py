import asyncio
import tornado.web
import tornado.gen
import tornado.httpserver
import os

class AnalyticsApp(tornado.web.RequestHandler):

    def prepare(self):
        self.set_header("Contet-Type", "application/json")
        self.set_header("charset", "UTF-8")

    def get(self):
        print('get...')
        self.write({"test": "get-pass"})

    def post(self):
        print('post....')
        self.write({"test": "post-pass"})

def make_app():
    print( 'just trying...')
    return tornado.web.Application(
        [
            (r"//v1/risk/calculate/bulk", AnalyticsApp),
            (r"/auth", AnalyticsApp)

        ]
   )

async def main():
    app = make_app()
    ssl_options = {
        "certfile": os.path.join(r"C:\Users\Surfer" , "cert.pem" ),
        "keyfile":  os.path.join(r"C:\Users\Surfer", "key.pem")
    }
    http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
    http_server.listen(8888)
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())