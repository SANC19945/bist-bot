import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime

TELEGRAM_BOT_TOKEN = "8616876708:AAEJ7eAubBOcW4VW7EO7Rixpx-qnevZS1bU"
TELEGRAM_CHAT_ID = "906997340"

def telegram_mesaj_gonder(mesaj):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram hatası: {e}")

def piyasa_listelerini_getir():
    bist_hisseleri = [
        "AEFES.IS", "AGHOL.IS", "AKBNK.IS", "AKENR.IS", "AKFGY.IS", "AKSA.IS", "AKSEN.IS", "ALARK.IS", "ALBRK.IS", "ALGYO.IS",
        "ALKIM.IS", "ARCLK.IS", "ASELS.IS", "ASTOR.IS", "ALFAS.IS", "AYDEM.IS", "BAGFS.IS", "BIMAS.IS", "BRYAT.IS", "BUCIM.IS",
        "CANTE.IS", "CCOLA.IS", "CEMTS.IS", "CIMSA.IS", "CWENE.IS", "DEVA.IS", "DOAS.IS", "DOHOL.IS", "ECILC.IS", "ECZYT.IS",
        "EGEEN.IS", "EKGYO.IS", "ENERY.IS", "ENKAI.IS", "EREGL.IS", "EUPWR.IS", "EUREN.IS", "FROTO.IS", "GARAN.IS", "GEDIK.IS",
        "GESAN.IS", "GLYHO.IS", "GUBRF.IS", "GWIND.IS", "HALKB.IS", "HEKTS.IS", "IPEKE.IS", "ISCTR.IS", "ISDMR.IS", "ISMEN.IS",
        "IZMDC.IS", "KCAER.IS", "KCHOL.IS", "KONTR.IS", "KONYA.IS", "KRDMD.IS", "KTLEV.IS", "KZBGY.IS", "MAVI.IS", "MGROS.IS",
        "ODAS.IS", "OYAKC.IS", "PETKM.IS", "PGSUS.IS", "PSGYO.IS", "QUAGR.IS", "REEDR.IS", "SAHOL.IS", "SASA.IS",
        "SDTTR.IS", "SISE.IS", "SKBNK.IS", "SMRTG.IS", "SOKM.IS", "TABGD.IS", "TAVHL.IS", "TCELL.IS", "THYAO.IS", "TKFEN.IS",
        "TMSN.IS", "TOASO.IS", "TSKB.IS", "TTKOM.IS", "TTRAK.IS", "TUPRS.IS", "ULKER.IS", "VAKBN.IS", "VESBE.IS", "VESTL.IS",
        "YEOTK.IS", "YKBNK.IS", "YYLGD.IS", "ZOREN.IS"
    ]
    
    abd_hisseleri = [
        "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "NFLX", "AMD", "INTC", 
        "PLTR", "COIN", "PYPL", "BA", "DIS", "NKE", "JPM", "V", "WMT", "SPY", "QQQ"
    ]

    avrupa_hisseleri = [
        "SAP.DE", "SIE.DE", "ALV.DE", "AIR.PA", "MC.PA", "TTE.PA", "OR.PA", "AZN.L", "SHEL.L", "HSBA.L"
    ]
    
    return bist_hisseleri, abd_hisseleri, avrupa_hisseleri

def teknik_indikatorleri_hesapla(df):
    # 1. SMA (5 ve 10)
    df['SMA5'] = df['Close'].rolling(window=5).mean()
    df['SMA10'] = df['Close'].rolling(window=10).mean()
    
    # 2. EMA (9 ve 21)
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # 3. RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 4. MACD (12, 26, 9)
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # 5. Bollinger Bands (20, 2)
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (std * 2)
    
    return df

def hisse_tara_ve_gonder(hisse_listesi, kategori_adi, para_birimi):
    bulunan_sinyaller = 0
    for hisse in hisse_listesi:
        try:
            df = yf.download(hisse, period="2mo", interval="1d", progress=False)
            if df.empty or len(df) < 30:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = teknik_indikatorleri_hesapla(df)
            
            son_fiyat = float(df['Close'].iloc[-1])
            rsi_deger = float(df['RSI'].iloc[-1])
            
            # Kesişim kontrolü (EMA 9 ve EMA 21 ana tetikleyici olarak alındı)
            dunku_ema9 = float(df['EMA9'].iloc[-2])
            bugunku_ema9 = float(df['EMA9'].iloc[-1])
            dunku_ema21 = float(df['EMA21'].iloc[-1] if 'EMA21' in df else df['EMA21'].iloc[-2]) # Güvenli index
            dunku_ema21 = float(df['EMA21'].iloc[-2])
            bugunku_ema21 = float(df['EMA21'].iloc[-1])

            macd_val = float(df['MACD'].iloc[-1])
            macd_sig = float(df['MACD_Signal'].iloc[-1])
            bb_upper = float(df['BB_Upper'].iloc[-1])
            bb_lower = float(df['BB_Lower'].iloc[-1])
            
            temiz_isim = hisse.replace(".IS", "").replace(".DE", " (Almanya)").replace(".PA", " (Fransa)").replace(".L", " (İngiltere)")

            # Al Sinyali (EMA 9 yukarı kesiyor ve MACD pozitif/kesişimde)
            if dunku_ema9 <= dunku_ema21 and bugunku_ema9 > bugunku_ema21:
                trend_durumu = "Güçlü Boğa (Alım Fırsatı)"
                risk_skoru = "Düşük" if rsi_deger < 60 else "Orta (Aşırı Alım Sınırı)"
                
                mesaj = (
                    f"🟢 *{kategori_adi} - ÇOKLU İNDİKATÖR AL SİNYALİ*\n\n"
                    f"🏢 *Varlık:* `{temiz_isim}`\n"
                    f"💰 *Fiyat:* `{son_fiyat:.2f} {para_birimi}`\n"
                    f"📈 *EMA Kesişimi:* EMA9 / EMA21 Yukarı Kesti\n"
                    f"⚡ *MACD Durumu:* `{'Pozitif (Alım Yönlü)' if macd_val > macd_sig else 'Nötr'}`\n"
                    f"📊 *RSI (14):* `{rsi_deger:.1f}`\n"
                    f"📉 *Bollinger Konumu:* `{'Alt Banda Yakın (Tepki)' if son_fiyat <= bb_lower * 1.02 else 'Normal Band İçinde'}`\n"
                    f"⚖️ *Risk Skoru:* `{risk_skoru}`\n"
                    f"🕒 *Zaman:* `{datetime.now().strftime('%d.%m.%Y %H:%M')}`"
                )
                telegram_mesaj_gonder(mesaj)
                bulunan_sinyaller += 1

            # Sat Sinyali (EMA 9 aşağı kesiyor)
            elif dunku_ema9 >= dunku_ema21 and bugunku_ema9 < bugunku_ema21:
                trend_durumu = "Ayı Eğilimi (Satış Baskısı)"
                risk_skoru = "Yüksek"
                
                mesaj = (
                    f"🔴 *{kategori_adi} - ÇOKLU İNDİKATÖR SAT SİNYALİ*\n\n"
                    f"🏢 *Varlık:* `{temiz_isim}`\n"
                    f"💰 *Fiyat:* `{son_fiyat:.2f} {para_birimi}`\n"
                    f"📉 *EMA Kesişimi:* EMA9 / EMA21 Aşağı Kesti\n"
                    f"⚡ *MACD Durumu:* `{'Negatif (Satış Yönlü)' if macd_val < macd_sig else 'Nötr'}`\n"
                    f"📊 *RSI (14):* `{rsi_deger:.1f}`\n"
                    f"📈 *Bollinger Konumu:* `{'Üst Banda Çarptı (Doygunluk)' if son_fiyat >= bb_upper * 0.98 else 'Normal Band İçinde'}`\n"
                    f"⚖️ *Risk Skoru:* `{risk_skoru}`\n"
                    f"🕒 *Zaman:* `{datetime.now().strftime('%d.%m.%Y %H:%M')}`"
                )
                telegram_mesaj_gonder(mesaj)
                bulunan_sinyaller += 1
        except Exception:
            pass
    return bulunan_sinyaller

def tum_piyasalari_tara():
    bist, abd, avrupa = piyasa_listelerini_getir()
    toplam_hisse = len(bist) + len(abd) + len(avrupa)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Kapsamlı indikatör taraması başladı. Varlık sayısı: {toplam_hisse}")
    
    s_bist = hisse_tara_ve_gonder(bist, "BIST 100", "TL")
    s_abd = hisse_tara_ve_gonder(abd, "ABD BORSALARI", "$")
    s_avrupa = hisse_tara_ve_gonder(avrupa, "AVRUPA BORSALARI", "€ / £")
    
    print(f"Tarama bitti. İletilen toplam sinyal: {s_bist + s_abd + s_avrupa}")

if __name__ == "__main__":
    tum_piyasalari_tara()
