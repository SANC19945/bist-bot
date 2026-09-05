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

def bist100_listesini_getir():
    return [
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

def tum_bist100_tara():
    hisseler = bist100_listesini_getir()
    print(f"BIST 100 taranıyor ({len(hisseler)} hisse)...")
    
    signal_sayisi = 0
    for hisse in hisseler:
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
            
            hisse_adi = hisse.replace(".IS", "")

            if dunku_sma5 <= dunku_sma10 and bugunku_sma5 > bugunku_sma10:
                mesaj = f"🟢 *BIST 100 AL SİNYALİ*\n\n🏢 *Hisse:* `{hisse_adi}`\n💰 *Fiyat:* `{son_fiyat:.2f} TL`\n📊 *Strateji:* SMA5 / SMA10 Yukarı Kesti"
                telegram_mesaj_gonder(mesaj)
                signal_sayisi += 1

            elif dunku_sma5 >= dunku_sma10 and bugunku_sma5 < bugunku_sma10:
                mesaj = f"🔴 *BIST 100 SAT SİNYALİ*\n\n🏢 *Hisse:* `{hisse_adi}`\n💰 *Fiyat:* `{son_fiyat:.2f} TL`\n📊 *Strateji:* SMA5 / SMA10 Aşağı Kesti"
                telegram_mesaj_gonder(mesaj)
                signal_sayisi += 1
                
        except Exception:
            pass

    print(f"Tarama bitti. Sinyal sayısı: {signal_sayisi}")

if __name__ == "__main__":
    tum_bist100_tara()
