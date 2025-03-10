from http.server import HTTPServer, SimpleHTTPRequestHandler
import os


class cors(SimpleHTTPRequestHandler):
    # end_headers メソッドのオーバーライド
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        return super().end_headers()

    # OPTIONS メソッド (CORS のプリフライトリクエストに使われます)
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    httpd = HTTPServer(("localhost", 8080), cors)
    httpd.serve_forever()
