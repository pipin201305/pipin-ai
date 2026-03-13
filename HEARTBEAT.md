# HEARTBEAT.md

1. **아침 8시 브리핑 (메일, 캘린더, 뉴스) 텔레그램 직배송**
   - 현재 시간이 KST(한국 표준시) 기준 오전 08:00 ~ 09:30 사이인지 확인.
   - `memory/briefing_date.txt` 파일에 기록된 날짜가 오늘 날짜(YYYY-MM-DD KST)와 다르다면:
     1) 세 가지 스크립트(이메일, 캘린더, 뉴스)의 출력 결과를 종합하여 아주 깔끔한 '아침 브리핑 메시지'를 작성한 뒤 이 방(텔레그램)으로 즉각 보고합니다. (인사말과 함께 주요 일정을 요약해 줄 것)
     2) 보고가 완료되면 오늘 날짜를 `memory/briefing_date.txt`에 덮어씁니다.

2. **30분 주기 업무 메일 감시 및 웹 대시보드 갱신**
   - **`python3 scripts/update_dashboard.py`** 를 실행하여 OpenClaw Web UI용 대시보드(`DASHBOARD.md`)를 백그라운드에서 최신화합니다.
   - **`python3 scripts/check_new_emails.py`** 를 실행합니다.
   - 출력 결과에 "🚨 [새로운 업무 메일 도착]"이 포함되어 있다면 그 내용을 파싱하여 이 채팅방에 즉각 보고합니다. 
   - 그 외의 경우("NO_NEW_BUSINESS_EMAILS")에는 조용히 넘어갑니다(HEARTBEAT_OK).