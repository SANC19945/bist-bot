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
    # 1. BIST 100 Hisseleri
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
    
    # 2. ABD Borsaları (S&P 500 / NASDAQ Devleri)
    abd_hisseleri = [
        "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "NFLX", "AMD", "INTC", 
        "PLTR", "COIN", "PYPL", "BA", "DIS", "NKE", "JPM", "V", "WMT", "SPY", "QQQ"
    ]

    # 3. Avrupa Borsaları (DAX 40 - Almanya, CAC 40 - Fransa, FTSE 100 - İngiltere Devleri)
    avrupa_hisseleri = [
        "SAP.DE", "SIE.DE", "ALV.DE", "AIR.PA", "MC.PA", "TTE.PA", "OR.PA", "AZN.L", "SHEL.L", "HSBA.L"
    ]
    
    return bist_hisseleri, abd_hisseleri, avrupa_hisseleri

def hisse_tara_ve_gonder(hisse_listesi, kategori_adi, para_birimi):
    bulunan_sinyaller = 0
    for hisse in hisse_listesi:
        try:
            df = yf.download(hisse, period="1mo", interval="1d", progress=False)
            if df.empty or len(df) < 15:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df['SMA5'] = df['Close'].rolling(window=5).mean()
            df['SMA10'] = df['Close'].rolling(window=10).mean()
            
            son_fiyat = float(df['Close'].iloc[-1])
            dunku_sma5 = float(df['SMA5'].iloc[-2])
            bugunku_sma5 = float(df['SMA5'].iloc[-1])
            dunku_sma10 = float(df['SMA10'].iloc[-2])
            bugunku_sma10 = float(df['SMA10'].iloc[-1])
            
            temiz_isim = hisse.replace(".IS", "").replace(".DE", " (Almanya)").replace(".PA", " (Fransa)").replace(".L", " (İngiltere)")

            # Al Sinyali
            if dunku_sma5 <= dunku_sma10 and bugunku_sma5 > bugunku_sma10:
                risk_puani = "Düşük (Güçlü Trend)" if son_fiyat > bugunku_sma5 else "Orta"
                mesaj = (
                    f"🟢 *{kategori_adi} AL SİNYALİ*\n\n"
                    f"🏢 *Varlık:* `{temiz_isim}`\n"
                    f"💰 *Fiyat:* `{son_fiyat:.2f} {para_birimi}`\n"
                    f"📊 *Kesişim:* SMA5 / SMA10 Yukarı\n"
                    f"⚖️ *Risk Skoru:* `{risk_puani}`\n"
                    f"🕒 *Zaman:* `{datetime.now().strftime('%d.%m.%Y %H:%M')}`"
                )
                telegram_mesaj_gonder(mesaj)
                bulunan_sinyaller += 1

            # Sat Sinyali
            elif dunku_sma5 >= dunku_sma10 and bugunku_sma5 < bugunku_sma10:
                risk_puani = "Yüksek (Düşüş Baskısı)"
                mesaj = (
                    f"🔴 *{kategori_adi} SAT SİNYALİ*\n\n"
                    f"🏢 *Varlık:* `{temiz_isim}`\n"
                    f"💰 *Fiyat:* `{son_fiyat:.2f} {para_birimi}`\n"
                    f"📊 *Kesişim:* SMA5 / SMA10 Aşağı\n"
                    f"⚖️ *Risk Skoru:* `{risk_puani}`\n"
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
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Küresel tarama başladı. Toplam varlık: {toplam_hisse}")
    
    s_bist = hisse_tara_ve_gonder(bist, "BIST 100", "TL")
    s_abd = hisse_tara_ve_gonder(abd, "ABD BORSALARI (S&P/Nasdaq)", "$")
    s_avrupa = hisse_tara_ve_gonder(avrupa, "AVRUPA BORSALARI (DAX/CAC/FTSE)", "€ / £")
    
    toplam_sinyal = s_bist + s_abd + s_avrupa
    print(f"Tarama tamamlandı. Gönderilen toplam sinyal: {toplam_sinyal}")

if __name__ == "__main__":
    tum_piyasalari_tara()
