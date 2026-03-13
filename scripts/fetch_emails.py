import imaplib
import email
from email.header import decode_header
import datetime
import os
import json

# config.json에서 정보 로드
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
        accounts = config.get('accounts', [])
except FileNotFoundError:
    print("❌ 설정 파일을 찾을 수 없습니다.")
    exit(1)

def fetch_morning_briefing():
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📬 통합 우편함 스캔을 시작합니다...\n")
    
    for account in accounts:
        acc_type = account.get('type')
        email_addr = account.get('email')
        password = account.get('password')
        server = account.get('server')
        
        print(f"==================================================")
        print(f"🛡️ [{acc_type}] {email_addr} 스캔 중...")
        
        try:
            mail = imaplib.IMAP4_SSL(server)
            mail.login(email_addr, password)
            mail.select('inbox')
            
            # 최근 24시간 이내의 안 읽은 메일(UNSEEN) 검색
            date_since = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'(UNSEEN SINCE {date_since})')
            
            email_ids = messages[0].split()
            
            if not email_ids:
                print(f"📭 {acc_type}에는 최근 24시간 내에 새로 도착한 안 읽은 메일이 없습니다.\n")
                mail.logout()
                continue

            print(f"총 {len(email_ids)}개의 안 읽은 새 메일이 있습니다.\n")
            
            # 최근 5개만 가져오기
            for e_id in email_ids[-5:]:
                status, msg_data = mail.fetch(e_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        subject, encoding = decode_header(msg['Subject'])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else 'utf-8', errors='ignore')
                        
                        sender, encoding = decode_header(msg.get('From'))[0]
                        if isinstance(sender, bytes):
                            sender = sender.decode(encoding if encoding else 'utf-8', errors='ignore')
                            
                        print(f"📌 [보낸사람] {sender}")
                        print(f"📝 [제목] {subject}")
                        print("-" * 50)
                        
            mail.logout()
            print("") # 간격 띄우기
            
        except Exception as e:
            print(f"❌ {acc_type} 메일을 가져오는 중 오류가 발생했습니다: {e}\n")

    print("✅ 모든 메일 브리핑이 완료되었습니다.")

if __name__ == '__main__':
    fetch_morning_briefing()
