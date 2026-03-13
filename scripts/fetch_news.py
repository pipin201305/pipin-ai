import urllib.request
import xml.etree.ElementTree as ET
import datetime

# 한국 표준시(KST) 설정
KST = datetime.timezone(datetime.timedelta(hours=9))

def fetch_news():
    now_kst = datetime.datetime.now(KST)
    print(f"[{now_kst.strftime('%Y-%m-%d %H:%M:%S')} KST] 📰 경제/부동산 주요 뉴스 스캔 중...\n")
    
    # 구글 뉴스 RSS (경제, 부동산 키워드, 최근 1일)
    url = "https://news.google.com/rss/search?q=%EA%B2%BD%EC%A0%9C+%EB%B6%80%EB%8F%99%EC%82%B0+when:1d&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        
        if not items:
            print("📭 현재 수집된 뉴스가 없습니다.")
            return
            
        print("==================================================")
        print("📈 [오늘의 경제/부동산 헤드라인 Top 5]")
        print("==================================================")
        
        for i, item in enumerate(items[:5]):
            title = item.find('title').text
            # 출처(언론사)가 제목 끝에 "- 언론사명" 형식으로 붙는 경우가 많음
            clean_title = title.rsplit(' - ', 1)[0] if ' - ' in title else title
            publisher = item.find('source').text if item.find('source') is not None else "구글뉴스"
            link = item.find('link').text
            
            print(f"🗞️ {i+1}. {clean_title} ({publisher})")
            print(f"🔗 {link}")
            print("-" * 50)
            
        print("\n✅ 뉴스 브리핑이 완료되었습니다.")
        
    except Exception as e:
        print(f"❌ 뉴스를 가져오는 중 오류가 발생했습니다: {e}")

if __name__ == '__main__':
    fetch_news()
