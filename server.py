import http.server
import random
import time
from prometheus_client import Gauge
from prometheus_client import Counter
from prometheus_client import start_http_server
from prometheus_client import Summary
from prometheus_client import Histogram

REQUESTS = Counter('hello_worlds_total',
        'Hello Worlds requested.')

EXCEPTIONS = Counter('hello_world_exceptions_total',
        'Exceptions serving Hello World.')

INPROGRESS = Gauge('hello_worlds_inprogress',
        'Number of Hello Worlds in progress.')

LAST = Gauge('hello_world_last_time_seconds',
        'The last time a Hello World was served.')

LATENCY = Summary('hello_world_latency_seconds',
        'Time for a request Hello World.')

#FOR SLAs quartiles
LATENCY_ = Histogram('hello_world_latency_seconds',
        'Time for a request Hello World.',
        buckets=[0.0001, 0.0002, 0.0005, 0.001, 0.01, 0.1])

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        start = time.time()
        REQUESTS.inc()
        INPROGRESS.inc()
        with EXCEPTIONS.count_exceptions():
          if random.random() < 0.2:
            raise Exception
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8"))
        self.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
        self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        LAST.set(time.time())
        INPROGRESS.dec()
        LATENCY.observe(time.time() - start)

if __name__ == "__main__":
    start_http_server(8000)
    server = http.server.HTTPServer(('0.0.0.0', 8001), MyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
         pass

    server.server_close()
    print('Server ended')
