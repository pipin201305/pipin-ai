import imaplib
import email
from email.header import decode_header
import datetime
import os
import json

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
seen_file = os.path.join(os.path.dirname(__file__), '..', 'memory', 'seen_emails.json')

try:
    with open(config_path, 'r') as f:
        config = json.load(f)
        accounts = config.get('accounts', [])
except Exception:
    accounts = []

# 기존에 알림을 보낸 메일 ID 저장용
try:
    if os.path.exists(seen_file):
        with open(seen_file, 'r') as f:
            seen_emails = json.load(f)
    else:
        seen_emails = []
except Exception:
    seen_emails = []

# 스팸/광고 필터링 키워드
AD_KEYWORDS = ['(광고)', '[광고]', '특가', '할인', '이벤트', '프로모션', '쿠폰', '혜택', '무료체험', '뉴스레터']
AD_SENDERS = ['newsletter', 'marketing', 'promotions', 'no-reply@youtube.com', 'noreply@']

def is_business_email(subject, sender):
    subject_lower = subject.lower()
    sender_lower = sender.lower()
    
    # 1. 제목에 광고성 키워드가 있으면 스킵
    for kw in AD_KEYWORDS:
        if kw in subject_lower:
            return False
            
    # 2. 발신자가 전형적인 마케팅/뉴스레터 주소면 스킵 (일부 no-reply는 서버 알림일 수 있으므로 예외 처리 필요하지만 1차 필터링)
    for fw in AD_SENDERS:
        if fw in sender_lower:
            return False
            
    return True

def check_new_emails():
    new_business_emails = []
    
    for account in accounts:
        acc_type = account.get('type')
        email_addr = account.get('email')
        password = account.get('password')
        server = account.get('server')
        
        try:
            mail = imaplib.IMAP4_SSL(server)
            mail.login(email_addr, password)
            mail.select('inbox')
            
            # 최근 안 읽은 메일 검색
            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            if not email_ids:
                mail.logout()
                continue
                
            for e_id in email_ids:
                e_id_str = f"{email_addr}_{e_id.decode()}"
                
                # 이미 알림을 보낸 메일이면 패스
                if e_id_str in seen_emails:
                    continue
                    
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
                            
                        # 필터링 로직 적용
                        if is_business_email(subject, sender):
                            new_business_emails.append({
                                'account': acc_type,
                                'sender': sender,
                                'subject': subject
                            })
                            
                        # 알림 보낸 목록에 추가 (광고든 업무든 읽은 것으로 처리해서 다음 턴에 스킵)
                        seen_emails.append(e_id_str)
                        
            mail.logout()
            
        except Exception as e:
            pass # 백그라운드 체크이므로 조용히 넘어감

    # 1000개 넘어가면 오래된 것 잘라내기 (메모리 관리)
    if len(seen_emails) > 1000:
        seen_emails[:] = seen_emails[-1000:]
        
    # 파일 업데이트
    os.makedirs(os.path.dirname(seen_file), exist_ok=True)
    with open(seen_file, 'w') as f:
        json.dump(seen_emails, f)
        
    # 결과 출력 (HEARTBEAT가 읽어갈 수 있도록)
    if new_business_emails:
        print("🚨 [새로운 업무 메일 도착]")
        for mail in new_business_emails:
            print(f"- [{mail['account']}] {mail['sender']} : {mail['subject']}")
    else:
        print("NO_NEW_BUSINESS_EMAILS")

if __name__ == '__main__':
    check_new_emails()
