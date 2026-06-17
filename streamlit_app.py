import streamlit as st
import requests
from bs4 import BeautifulSoup
import re


st.set_page_config(page_title='8bitHome', page_icon=':bar_chart:')


def fetch_google_price(path: str):
    """Fetch current price and percent change from Google Finance quote path.

    `path` examples:
    - 'SOXL:NYSEARCA' -> https://www.google.com/finance/quote/SOXL:NYSEARCA
    - 'USD-KRW' -> https://www.google.com/finance/quote/USD-KRW
    Returns dict {'last': float, 'pct': float or None} or None on failure.
    """
    url = f'https://www.google.com/finance/quote/{path}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        # Price is often in a div with class containing 'YMlKec'
        price_tag = soup.find('div', class_=re.compile('YMlKec'))
        last = None
        if price_tag:

            num = num.replace('\n', '')
            text = price_tag.get_text().strip()
            # Remove any non-digit/decimal/minus characters
            cleaned = text.replace(',', '')
            num = re.sub(r'[^0-9\.\-]', '', cleaned)
            try:
                last = float(num) if num else None
            except Exception:
                last = None

        # Percent change: look for span with class containing 'WlRRw' or 'IsqQVc'
        pct = None
        pct_tag = soup.find(['div', 'span'], class_=re.compile('(WlRRw|IsqQVc|PZPZlf)'))
        if pct_tag:
            pct_text = pct_tag.get_text()
            m = re.search(r'([+-]?\d+[\.,]?\d*)%', pct_text)
            if m:
                pct = float(m.group(1).replace(',', '.'))

        return {'last': last, 'pct': pct}
    except Exception:
        return None


def render_page():
    st.title('SOXL 종가 및 USD/KRW 환율 (Google Finance)')
    st.write('데이터 소스: Google Finance (스크래핑 방식). 실시간성이 완벽히 보장되지 않을 수 있습니다.')

    col1, col2 = st.columns(2)

    soxl = fetch_google_price('SOXL:NYSEARCA')
    usdkrw = fetch_google_price('USD-KRW')

    if soxl and soxl['last'] is not None:
        col1.metric('SOXL (종가)', f"{soxl['last']:,}", f"{soxl['pct']:+.2f}%" if soxl['pct'] is not None else '')
    else:
        col1.write('SOXL 데이터 불러오기 실패')

    if usdkrw and usdkrw['last'] is not None:
        col2.metric('USD / KRW', f"{usdkrw['last']:,}", f"{usdkrw['pct']:+.2f}%" if usdkrw['pct'] is not None else '')
    else:
        col2.write('USD/KRW 데이터 불러오기 실패')


if __name__ == '__main__':
    render_page()
    st.divider()
