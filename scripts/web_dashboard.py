import os
import json
import subprocess
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8080
WORKSPACE = "/home/pipin201305/.openclaw/workspace"

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # 데이터 수집
        emails = self.run_script("fetch_emails.py")
        calendar = self.run_script("fetch_calendar.py")
        news = self.run_script("fetch_news.py")
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")

        html = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>박비서 통합 대시보드</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background-color: #f8f9fa; font-family: 'Pretendard', sans-serif; }}
                .card {{ border: none; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }}
                .header-section {{ background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%); color: white; padding: 40px 0; border-radius: 0 0 30px 30px; margin-bottom: 30px; }}
                pre {{ background: #f1f1f1; padding: 15px; border-radius: 10px; font-size: 0.9rem; white-space: pre-wrap; }}
                .status-badge {{ font-size: 0.8rem; padding: 5px 10px; border-radius: 20px; background: #e9ecef; }}
            </style>
        </head>
        <body>
            <div class="header-section text-center">
                <h1>📊 피플 AI 통합 대시보드</h1>
                <p>보스 전용 스마트 오피스 관제 센터</p>
                <span class="status-badge">마지막 갱신: {now} (KST)</span>
            </div>
            
            <div class="container">
                <div class="row">
                    <!-- 메일 섹션 -->
                    <div class="col-md-6">
                        <div class="card p-4">
                            <h3 class="mb-3">📬 최신 메일 브리핑</h3>
                            <pre>{emails}</pre>
                        </div>
                    </div>
                    
                    <!-- 일정 섹션 -->
                    <div class="col-md-6">
                        <div class="card p-4">
                            <h3 class="mb-3">📅 주요 일정 (통합)</h3>
                            <pre>{calendar}</pre>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <!-- 뉴스 섹션 -->
                    <div class="col-12">
                        <div class="card p-4">
                            <h3 class="mb-3">📰 경제/부동산 주요 뉴스</h3>
                            <pre>{news}</pre>
                        </div>
                    </div>
                </div>
                
                <div class="text-center mt-4 text-muted pb-5">
                    <p>© 2026 박비서 (Park Assistant) - Senior AI Office Manager</p>
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

    def run_script(self, script_name):
        try:
            path = os.path.join(WORKSPACE, "scripts", script_name)
            result = subprocess.run(["python3", path], capture_output=True, text=True)
            return result.stdout if result.stdout else "데이터가 없습니다."
        except Exception as e:
            return f"오류 발생: {e}"

def run_server():
    server = HTTPServer(('0.0.0.0', PORT), DashboardHandler)
    print(f"대시보드 서버가 {PORT} 포트에서 시작되었습니다...")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
