import urllib.request
import datetime
import os
import json

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
        calendars = config.get('calendars', [])
except Exception:
    calendars = []

if not calendars:
    print("❌ 캘린더 URL이 설정되지 않았습니다.")
    exit(1)

# 한국 표준시(KST) 설정 (UTC+9)
KST = datetime.timezone(datetime.timedelta(hours=9))

def parse_ics():
    now_kst = datetime.datetime.now(KST)
    print(f"[{now_kst.strftime('%Y-%m-%d %H:%M:%S')} KST] 📅 통합 구글 캘린더 스캔을 시작합니다...\n")
    
    today_str = now_kst.strftime("%Y%m%d")
    all_upcoming = []

    for cal in calendars:
        cal_name = cal.get('name')
        cal_url = cal.get('url')
        print(f"==================================================")
        print(f"🛡️ [{cal_name}] 캘린더 스캔 중...")
        
        try:
            req = urllib.request.Request(cal_url)
            with urllib.request.urlopen(req) as response:
                data = response.read().decode('utf-8')
                
            events = []
            current_event = {}
            in_event = False
            
            for line in data.splitlines():
                line = line.strip()
                if line.startswith('BEGIN:VEVENT'):
                    in_event = True
                    current_event = {}
                elif line.startswith('END:VEVENT'):
                    in_event = False
                    if 'SUMMARY' in current_event and 'DTSTART' in current_event:
                        current_event['CALENDAR'] = cal_name
                        events.append(current_event)
                elif in_event:
                    if line.startswith('SUMMARY:'):
                        current_event['SUMMARY'] = line.split(':', 1)[1]
                    elif line.startswith('DTSTART'):
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            current_event['DTSTART'] = parts[1]
                            
            if not events:
                print(f"📭 {cal_name} 캘린더에 등록된 일정이 없습니다.\n")
                continue

            # KST 날짜 기준으로 다가오는 일정 필터링
            upcoming = []
            for e in events:
                dt_raw = e['DTSTART']
                if dt_raw[:8] >= today_str:
                    upcoming.append(e)
            
            all_upcoming.extend(upcoming)
            print(f"✅ {len(upcoming)}개의 다가오는 일정이 확인되었습니다.\n")
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"❌ {cal_name} 달력 주소를 찾을 수 없습니다. (비공개 주소가 맞는지 확인해 주세요)\n")
            else:
                print(f"❌ {cal_name} 캘린더를 가져오는 중 HTTP 오류 발생: {e}\n")
        except Exception as e:
            print(f"❌ {cal_name} 캘린더를 가져오는 중 오류 발생: {e}\n")

    if not all_upcoming:
        print("📭 전체 캘린더에 다가오는 일정이 없습니다.")
        return

    all_upcoming.sort(key=lambda x: x['DTSTART'])
    print("==================================================")
    print(f"📢 [통합 브리핑] 총 {len(all_upcoming)}개의 다가오는 일정 (가장 가까운 5개)")
    print("==================================================")
    
    for e in all_upcoming[:5]:
        dt_raw = e.get('DTSTART')
        is_utc = dt_raw.endswith('Z')
        clean_dt = dt_raw.replace('Z', '')
        
        if len(clean_dt) >= 15 and 'T' in clean_dt:
            try:
                dt_obj = datetime.datetime.strptime(clean_dt, "%Y%m%dT%H%M%S")
                # UTC 시간(Z가 붙은 경우) KST(+9)로 변환
                if is_utc:
                    dt_obj = dt_obj.replace(tzinfo=datetime.timezone.utc).astimezone(KST)
                dt_fmt = dt_obj.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                dt_fmt = clean_dt
        elif len(clean_dt) == 8:
            dt_fmt = f"{clean_dt[:4]}-{clean_dt[4:6]}-{clean_dt[6:8]} (종일)"
        else:
            dt_fmt = clean_dt
            
        print(f"📌 [일정] {e.get('SUMMARY')} (출처: {e.get('CALENDAR')})")
        print(f"🕒 [시간] {dt_fmt} (KST)")
        print("-" * 50)
        
    print("\n✅ 통합 캘린더 브리핑이 완료되었습니다.")

if __name__ == '__main__':
    parse_ics()
