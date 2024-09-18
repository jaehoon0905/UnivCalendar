# Academic Calendar to ics file
import requests
import bs4
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import sys

API_URL = 'https://www.gachon.ac.kr/schdulmanage/kor/25/monthSchdul.do'
data = {
    'kind':'nextMonth',
    'year':'2024',
    'month':'01',
    'schdulType':'MONTH',
}

def main():
    if len(sys.argv) != 2:
        print("Usage: python cal.py <CURRENT YEAR>")
        sys.exit(1)

    YEAR = sys.argv[1]
    data['year'] = YEAR
    suffix = YEAR
    filename = 'Academic Calendar' + '_' + suffix

    cal = Calendar()

    for month_cursor in range(1, 12):   # 2월~12월 일정
        data['month'] = str(month_cursor).zfill(2)
        response = requests.post(url=API_URL, data=data)
        obj = bs4.BeautifulSoup(response.text, 'lxml')
        for item in obj.select_one('.sche-comt').select('tr'):
            date = item.select_one('th').get_text().strip()
            desc = item.select_one('td').get_text().strip().replace('\n', '').replace('\\', '')
            print(date, desc)

            event = Event()
            event.add('summary', desc + ' ' + suffix)

            if '~' in date: # 여러 날 일정
                print('date', date)
                start_date = date.split(' ~ ')[0]
                start_month = int(start_date.split('.')[0])
                start_day = int(start_date.split('.')[1])
                end_date = date.split(' ~ ')[-1]
                end_month = int(end_date.split('.')[0])
                end_day = int(end_date.split('.')[1])
                if start_month > end_month and start_month > int(data['month']): # 전년에서 넘어오는 일정 처리
                    start_date = datetime(int(YEAR)-1, start_month, start_day, 0, 0, 0, tzinfo=pytz.timezone('Asia/Seoul'))
                else:
                    start_date = datetime(int(YEAR), start_month, start_day, 0, 0, 0, tzinfo=pytz.timezone('Asia/Seoul'))

                if start_month > end_month and start_month < int(data['month']): # 차년도로 넘어가는 일정 처리
                    end_date = datetime(int(YEAR)+1, end_month, end_day, 0, 0, 0, tzinfo=pytz.timezone('Asia/Seoul'))
                else:
                    end_date = datetime(int(YEAR), end_month, end_day, 0, 0, 0, tzinfo=pytz.timezone('Asia/Seoul'))
            else:
                start_month = int(date.split('.')[0])
                start_day = int(date.split('.')[1])
                end_date = datetime(int(YEAR), start_month, start_day, 0, 0, 0, tzinfo=pytz.timezone('Asia/Seoul'))
                start_date = datetime(int(YEAR), start_month, start_day, 0, 0, 0, tzinfo=pytz.timezone('Asia/Seoul'))

            end_date = end_date + timedelta(days=1)  # 하루 종일 일정 -> end_date를 익일 자정으로 설정
            event.add('dtstart', start_date)
            event.add('dtend', end_date)

            # 캘린더에 이벤트 추가
            cal.add_component(event)
            print(start_date)
            print(end_date)

    with open(filename + '.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    main()
