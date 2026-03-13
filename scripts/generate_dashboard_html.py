import os
import subprocess
import datetime

WORKSPACE = "/home/pipin201305/.openclaw/workspace"
KST = datetime.timezone(datetime.timedelta(hours=9))

def run_script(script_name):
    try:
        path = os.path.join(WORKSPACE, "scripts", script_name)
        result = subprocess.run(["python3", path], capture_output=True, text=True, timeout=30)
        return result.stdout if result.stdout else "데이터가 없습니다."
    except Exception as e:
        return f"오류 발생: {e}"

def generate_static_dashboard():
    now_kst = datetime.datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    
    print("데이터 수집 중...")
    emails = run_script("fetch_emails.py")
    calendar = run_script("fetch_calendar.py")
    news = run_script("fetch_news.py")

    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>박비서 통합 대시보드</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; font-family: 'Pretendard', sans-serif; padding-top: 20px; }}
            .card {{ border: none; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .header-section {{ background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%); color: white; padding: 30px 15px; border-radius: 20px; margin-bottom: 30px; }}
            pre {{ background: #f1f1f1; padding: 15px; border-radius: 10px; font-size: 0.85rem; white-space: pre-wrap; word-break: break-all; }}
            .status-badge {{ font-size: 0.75rem; padding: 5px 12px; border-radius: 20px; background: rgba(255,255,255,0.2); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-section text-center">
                <h1 class="h3">📊 피플 AI 통합 대시보드</h1>
                <p class="mb-2">보스 전용 스마트 오피스 관제 센터</p>
                <span class="status-badge">마지막 갱신: {now_kst} (KST)</span>
            </div>
            
            <div class="row">
                <div class="col-lg-6">
                    <div class="card p-3">
                        <h5 class="mb-3">📬 최근 메일 브리핑</h5>
                        <pre>{emails}</pre>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="card p-3">
                        <h5 class="mb-3">📅 주요 일정 (통합)</h5>
                        <pre>{calendar}</pre>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="card p-3">
                        <h5 class="mb-3">📰 경제/부동산 주요 뉴스</h5>
                        <pre>{news}</pre>
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-3 text-muted pb-4" style="font-size: 0.8rem;">
                <p>© 2026 박비서 (Park Assistant)</p>
            </div>
        </div>
        <script>
            // 5분마다 자동 새로고침
            setTimeout(function() {{ location.reload(); }}, 300000);
        </script>
    </body>
    </html>
    """
    
    output_path = os.path.join(WORKSPACE, "scripts", "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 대시보드 생성 완료: {output_path}")

if __name__ == "__main__":
    generate_static_dashboard()
