"""
Live metal price fetcher — ALL elements.
Sources: Westmetall (LME), Silver (6-source chain), TradingEconomics (Mg, Li, Mn, Ti, Si)
"""
import re, requests
from bs4 import BeautifulSoup
from config import MINOR_ELEMENT_DEFAULTS

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
TIMEOUT = 15
LIVE = 'live'; ESTIMATED = 'estimated'; STATIC = 'static'; FALLBACK = 'fallback'

def _fetch_usdcny_rate():
    for url in ["https://open.er-api.com/v6/latest/USD", "https://api.exchangerate-api.com/v4/latest/USD"]:
        try:
            data = requests.get(url, headers=HEADERS, timeout=TIMEOUT).json()
            if 'rates' in data and 'CNY' in data['rates']:
                return float(data['rates']['CNY'])
        except Exception: pass
    return 7.25

def _fetch_westmetall(field):
    url = f"https://www.westmetall.com/en/markdaten.php?action=table&field={field}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT); resp.raise_for_status()
        for table in BeautifulSoup(resp.text, 'html.parser').find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    dt, pt = cells[0].get_text(strip=True), cells[1].get_text(strip=True)
                    if re.match(r'\d{2}\.\s', dt):
                        try:
                            p = float(pt.replace(',','').replace(' ',''))
                            if p > 100: return p, dt
                        except ValueError: continue
        return None, "Could not parse"
    except requests.RequestException as e: return None, str(e)

def fetch_lme_prices():
    metals = {'Al':'LME_Al_cash','Cu':'LME_Cu_cash','Zn':'LME_Zn_cash','Ni':'LME_Ni_cash'}
    results, notes, errors = {}, [], []
    for metal, field in metals.items():
        price, info = _fetch_westmetall(field)
        if price: results[metal] = price; notes.append(f"{metal}: ${price:,.1f}/t (Westmetall {info})")
        else: errors.append(f"⚠️ {metal}: Westmetall failed — {info}"); results[metal] = None
    return {'prices': results, 'notes': notes, 'errors': errors}

def _fetch_tradingeconomics(commodity):
    try:
        text = requests.get(f"https://tradingeconomics.com/commodity/{commodity}", headers=HEADERS, timeout=TIMEOUT).text
        for pat in [r'(?:rose|fell|decreased|increased|climbed|dropped|was|traded|at|to)\s+(?:to\s+)?(?:about\s+)?(?:below\s+)?(?:above\s+)?([0-9,]+\.?\d*)\s*(USD|CNY|EUR)/(T|t|Ton|Tonne|KG|kg|Lbs|lbs)',
                    r'([0-9,]+\.?\d*)\s*(USD|CNY|EUR)/(T|t|Ton|Tonne|KG|kg|Lbs|lbs)']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                price = float(m.group(1).replace(',',''))
                cur, unit = m.group(2).upper(), m.group(3).upper()
                u = f"{cur}/{'t' if unit in ('T','TON','TONNE') else 'kg' if unit=='KG' else 'lb'}"
                dm = re.search(r'on\s+(\w+\s+\d{1,2},?\s+\d{4})', text)
                return price, u, dm.group(1) if dm else "recent"
        return None, None, "Could not parse"
    except Exception as e: return None, None, str(e)

def _convert_to_usd_per_kg(price, unit_str, usdcny):
    if not price or not unit_str: return None
    u = unit_str.upper()
    curr = 1.0/usdcny if 'CNY' in u else (1.0 if 'USD' in u else (1.10 if 'EUR' in u else None))
    wt = 1/1000 if '/T' in u else (1.0 if '/KG' in u else (2.20462 if '/LB' in u else None))
    return price * curr * wt if curr and wt else None

def _fetch_silver_metals_api():
    try:
        data = requests.get("https://data-asg.goldprice.org/dbXRates/USD", headers=HEADERS, timeout=TIMEOUT).json()
        for item in data.get('items',[]):
            if 'xagPrice' in item:
                p = float(item['xagPrice'])
                if 10 < p < 500: return p
    except: pass
    return None

def _fetch_silver_bullioncom():
    try:
        text = requests.get("https://www.bullion.com/spotprices/silver-price", headers=HEADERS, timeout=TIMEOUT).text
        for pat in [r'Current Spot Price[^$]*\$([0-9]+\.[0-9]{2})', r'Ask\s*\$([0-9]+\.[0-9]{2})', r'"price":\s*"?\$?([0-9]+\.[0-9]{2})']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                p = float(m.group(1))
                if 10 < p < 500: return p
    except: pass
    return None

def _fetch_silver_apmex():
    try:
        text = requests.get("https://www.apmex.com/silver-price", headers=HEADERS, timeout=TIMEOUT).text
        for pat in [r'spot price[^$]*\$([0-9]+\.[0-9]{2})', r'"price":\s*"?([0-9]+\.[0-9]{2})', r'\$([0-9]+\.[0-9]{2})\s*/\s*oz']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                p = float(m.group(1))
                if 10 < p < 500: return p
    except: pass
    return None

def _fetch_silver_jmbullion():
    try:
        text = requests.get("https://www.jmbullion.com/charts/silver-prices/", headers=HEADERS, timeout=TIMEOUT).text
        for pat in [r'live Silver spot price[^$]*\$([0-9]+\.[0-9]{2})', r'Silver spot price[^$]*\$([0-9]+\.[0-9]{2})', r'"spotPrice":\s*([0-9]+\.[0-9]{2})']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                p = float(m.group(1))
                if 10 < p < 500: return p
    except: pass
    return None

def _fetch_silver_goldpricez():
    try:
        text = requests.get("https://goldpricez.com/silver-rates/us/ounce", headers=HEADERS, timeout=TIMEOUT).text
        for pat in [r'Price per Ounce is \$([0-9]+\.?\d*)', r'Silver Price[^$]*\$([0-9]+\.[0-9]{2})']:
            m = re.search(pat, text)
            if m:
                p = float(m.group(1))
                if 10 < p < 500: return p
    except: pass
    return None

def _fetch_silver_fortune():
    try:
        text = requests.get("https://fortune.com/article/current-price-of-silver/", headers=HEADERS, timeout=TIMEOUT, allow_redirects=True).text
        for pat in [r'silver[^$]{0,60}\$([0-9]+\.[0-9]{2})\s*per ounce', r'\$([0-9]+\.[0-9]{2})\s*per ounce']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                p = float(m.group(1))
                if 10 < p < 500: return p
    except: pass
    return None

def fetch_silver_price():
    tried = []
    for name, func in [("goldprice.org API",_fetch_silver_metals_api),("Bullion.com",_fetch_silver_bullioncom),
                        ("APMEX",_fetch_silver_apmex),("JM Bullion",_fetch_silver_jmbullion),
                        ("goldpricez",_fetch_silver_goldpricez),("Fortune",_fetch_silver_fortune)]:
        try:
            p = func()
            if p: return {'price':p,'source':name,'note':f"Ag: ${p:.2f}/oz ({name})",'errors':[]}
        except: pass
        tried.append(name)
    return {'price':None,'source':None,'note':'','errors':[f"⚠️ Silver: all {len(tried)} sources failed."]}

def fetch_all_prices():
    sources, all_notes, all_errors = {}, [], []
    lme = fetch_lme_prices(); prices = lme['prices']; all_notes.extend(lme['notes']); all_errors.extend(lme['errors'])
    for m in ('Al','Cu','Zn','Ni'):
        sources[m] = (LIVE,"Westmetall LME Cash") if prices.get(m) else (FALLBACK,"Westmetall failed")
    ag = fetch_silver_price()
    if ag['price']: prices['Ag_oz']=ag['price']; all_notes.append(ag['note']); sources['Ag_oz']=(LIVE,f"Spot via {ag['source']}")
    else: prices['Ag_oz']=None; all_errors.extend(ag['errors']); sources['Ag_oz']=(FALLBACK,"All silver sources failed")
    usdcny = _fetch_usdcny_rate(); all_notes.append(f"USD/CNY: {usdcny:.2f}")
    for elem,(slug,desc) in {'Mg':('magnesium','Mg ingot 99.9%'),'Mn':('manganese','Mn 99.7%'),'Ti':('titanium','Ti sponge'),'Si':('silicon','Si 553')}.items():
        raw,unit,dt = _fetch_tradingeconomics(slug)
        if raw and unit:
            usd_kg = _convert_to_usd_per_kg(raw, unit, usdcny)
            if usd_kg and usd_kg > 0:
                prices[elem]=round(usd_kg,2); all_notes.append(f"{elem}: {raw:,.0f} {unit} ({dt}) → ${usd_kg:.2f}/kg")
                sources[elem]=(ESTIMATED,f"TradingEcon {desc} ({raw:,.0f} {unit} → ${usd_kg:.2f}/kg)"); continue
        prices[elem]=MINOR_ELEMENT_DEFAULTS[elem]; all_errors.append(f"⚠️ {elem}: failed, default ${MINOR_ELEMENT_DEFAULTS[elem]}/kg")
        sources[elem]=(STATIC,f"Default ${MINOR_ELEMENT_DEFAULTS[elem]}/kg")
    li_raw,li_unit,li_dt = _fetch_tradingeconomics('lithium')
    if li_raw and li_unit:
        li_c = _convert_to_usd_per_kg(li_raw, li_unit, usdcny)
        if li_c:
            li_m=round(li_c*10,0); prices['Li']=li_m
            all_notes.append(f"Li: carb {li_raw:,.0f} {li_unit} → ${li_c:.2f}/kg carb → ~${li_m:.0f}/kg metal (×10)")
            sources['Li']=(ESTIMATED,f"TradingEcon Li₂CO₃ ×10 → ${li_m:.0f}/kg metal")
        else: prices['Li']=MINOR_ELEMENT_DEFAULTS['Li']; sources['Li']=(STATIC,f"Default ${MINOR_ELEMENT_DEFAULTS['Li']}/kg")
    else: prices['Li']=MINOR_ELEMENT_DEFAULTS['Li']; all_errors.append("⚠️ Li: failed"); sources['Li']=(STATIC,f"Default ${MINOR_ELEMENT_DEFAULTS['Li']}/kg")
    prices['Zr']=MINOR_ELEMENT_DEFAULTS['Zr']; sources['Zr']=(STATIC,"USGS $35/kg — stable")
    prices['Fe']=MINOR_ELEMENT_DEFAULTS['Fe']; sources['Fe']=(STATIC,"Nominal $0.10/kg")
    for k,fb in {'Al':3300,'Cu':12000,'Zn':3100,'Ni':17000,'Ag_oz':70}.items():
        if prices.get(k) is None: prices[k]=fb; sources[k]=(FALLBACK,f"Fallback ${fb}"); all_errors.append(f"Fallback {k}: ${fb}")
    return {'prices':prices,'sources':sources,'notes':'\n'.join(all_notes),'errors':all_errors}
