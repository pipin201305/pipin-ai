import http.server
import socketserver
import os

PORT = 8888
DIRECTORY = "/home/pipin201305/.openclaw/workspace/scripts"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

if __name__ == "__main__":
    # 기존 서버 프로세스가 있다면 종료 (생략 가능하나 안전을 위해)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"정적 서버 가동 중: 포트 {PORT}")
        httpd.serve_forever()
