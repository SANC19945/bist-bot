import os
import time
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone

TELEGRAM_BOT_TOKEN = "8616876708:AAEJ7eAubBOcW4VW7EO7Rixpx-qnevZS1bU"
TELEGRAM_CHAT_ID = "906997340"

ISIM_SOZLUGU = {
    # Kriptolar
    "BTC-USD": "Bitcoin (BTC)", "ETH-USD": "Ethereum (ETH)", "SOL-USD": "Solana (SOL)",
    "XRP-USD": "Ripple (XRP)", "AVAX-USD": "Avalanche (AVAX)", "DOGE-USD": "Dogecoin (DOGE)",
    "BNB-USD": "Binance Coin (BNB)", "ADA-USD": "Cardano (ADA)", "NEAR-USD": "Near Protocol (NEAR)",
    # ABD Hisseleri & ETF
    "AAPL": "Apple Inc. (ABD)", "MSFT": "Microsoft Corp. (ABD)", "NVDA": "NVIDIA Corp. (ABD)",
    "TSLA": "Tesla Inc. (ABD)", "AMZN": "Amazon.com (ABD)", "GOOGL": "Alphabet / Google (ABD)",
    "META": "Meta Platforms (ABD)", "NFLX": "Netflix Inc. (ABD)", "AMD": "AMD (ABD)", "PLTR": "Palantir Tech (ABD)",
    "SPY": "SPDR S&P 500 ETF (ABD)", "QQQ": "Invesco QQQ Trust (ABD)", "VOO": "Vanguard S&P 500 ETF",
    "GLD": "SPDR Gold Shares (Altın ETF)", "SLV": "iShares Silver Trust (Gümüş ETF)",
    # Yerli Fonlar (TEFAS)
    "MAC.IS": "Marmara Capital Hisse Senedi Fonu", "TTE.IS": "İş Portföy BIST 100 Dışı Şirketler Fonu",
    "TI2.IS": "İş Portföy Teknoloji Sektörleri Fonu", "IDH.IS": "İstanbul Portföy Birinci Hisse Fonu",
    "MAC": "Marmara Capital Hisse Senedi Fonu", "TTE": "İş Portföy BIST 100 Dışı Şirketler Fonu",
    # Avrupa
    "SAP.DE": "SAP SE (Almanya)", "SIE.DE": "Siemens AG (Almanya)", "AIR.PA": "Airbus SE (Fransa)"
}

last_update_id = 0

def get_turkey_time():
    tr_tz = timezone(timedelta(hours=3))
    return datetime.now(tr_tz)

def telegram_mesaj_gonder(mesaj):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
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
        "AKBNK.IS", "AKSA.IS", "AKSEN.IS", "ALARK.IS", "ARCLK.IS", "ASELS.IS", "ASTOR.IS", "BIMAS.IS",
        "EKGYO.IS", "ENKAI.IS", "EREGL.IS", "FROTO.IS", "GARAN.IS", "GESAN.IS", "GUBRF.IS", "HALKB.IS",
        "HEKTS.IS", "ISCTR.IS", "KCHOL.IS", "KONTR.IS", "KRDMD.IS", "MGROS.IS", "ODAS.IS", "PETKM.IS",
        "PGSUS.IS", "SAHOL.IS", "SASA.IS", "SISE.IS", "SOKM.IS", "TAVHL.IS", "TCELL.IS", "THYAO.IS",
        "TOASO.IS", "TTKOM.IS", "TUPRS.IS", "VAKBN.IS", "VESTL.IS", "YKBNK.IS"
    ]
    abd_hisseleri = [
        "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "NFLX", "AMD", "PLTR", "COIN", "INTC"
    ]
    avrupa_hisseleri = [
        "SAP.DE", "SIE.DE", "ALV.DE", "AIR.PA", "MC.PA", "TTE.PA", "AZN.L", "SHEL.L"
    ]
    etf_listesi = [
        "SPY", "QQQ", "VOO", "ARKK", "GLD", "SLV", "TLT"
    ]
    yerli_fonlar = [
        "MAC.IS", "TTE.IS", "TI2.IS", "IDH.IS"
    ]
    kriptolar = [
        "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "AVAX-USD", "DOGE-USD", "NEAR-USD"
    ]
    return bist_hisseleri, abd_hisseleri, avrupa_hisseleri, etf_listesi, yerli_fonlar, kriptolar

def teknik_indikatorleri_hesapla(df):
    df['SMA5'] = df['Close'].rolling(window=5).mean()
    df['SMA10'] = df['Close'].rolling(window=10).mean()
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (std * 2)
    return df

def evrensel_hisse_bul(hisse_kodu):
    code = hisse_kodu.upper().strip()
    
    adaylar = [
        code,
        code + "-USD",
        code + ".IS",
        code + ".TEFAS"
    ]
    
    for aday in adaylar:
        try:
            df_test = yf.download(aday, period="5d", progress=False)
            if not df_test.empty and len(df_test) > 0:
                return aday
        except:
            continue
    return code

def evrensel_analiz_et(hisse_kodu):
    symbol = evrensel_hisse_bul(hisse_kodu)

    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if df.empty or len(df) < 15:
            return f"❌ *{hisse_kodu}* için yeterli veri bulunamadı. Kodu kontrol edin (Örn: `thyao`, `eth`, `mac`, `aapl`)."
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = teknik_indikatorleri_hesapla(df)
        
        son_fiyat = float(df['Close'].iloc[-1])
        rsi_deger = float(df['RSI'].iloc[-1])
        bugunku_ema9 = float(df['EMA9'].iloc[-1])
        bugunku_ema21 = float(df['EMA21'].iloc[-1])
        macd_val = float(df['MACD'].iloc[-1])
        macd_sig = float(df['MACD_Signal'].iloc[-1])
        bb_upper = float(df['BB_Upper'].iloc[-1])
        bb_lower = float(df['BB_Lower'].iloc[-1])
        
        temiz_isim = ISIM_SOZLUGU.get(symbol, ISIM_SOZLUGU.get(hisse_kodu.upper(), symbol))
        su_anki_zaman = get_turkey_time().strftime('%d.%m.%Y %H:%M')

        trend_pozitif = bugunku_ema9 > bugunku_ema21
        trend = "Yükseliş (Boğa) Trendi 🟢" if trend_pozitif else "Düşüş (Ayı) Trendi 🔴"

        if rsi_deger > 70:
            rsi_durum = "Aşırı Alım Bölgesinde ⚠️"
        elif rsi_deger < 30:
            rsi_durum = "Aşırı Satım Bölgesinde (Fırsat) 💡"
        else:
            rsi_durum = "Normal Bantta 📊"

        if trend_pozitif and rsi_deger <= 65 and macd_val > macd_sig:
            tavsiye = "GÜÇLÜ AL 🟢 (Yükseliş Trendi & Destekli)"
            risk = "Düşük / Orta"
        elif trend_pozitif and rsi_deger > 70:
            tavsiye = "TUT / KÂR AL 🟡 (Aşırı Alım Sınırında)"
            risk = "Orta - Yüksek"
        elif not trend_pozitif and rsi_deger < 35:
            tavsiye = "TUT / İZLE 🟡 (Dip Arayışı / Destek)"
            risk = "Orta"
        elif not trend_pozitif and rsi_deger >= 35:
            tavsiye = "SAT / UZAK DUR 🔴 (Düşüş Trendi Baskın)"
            risk = "Yüksek"
        else:
            tavsiye = "TUT / BEKLE ⚖️ (Yatay / Kararsız Seyir)"
            risk = "Dengeli / Orta"

        rapor = (
            f"🎯 *DETAYLI VARLIK ANALİZİ VE KARAR*\n\n"
            f"🏢 *Varlık:* `{temiz_isim}`\n"
            f"💰 *Güncel Fiyat:* `{son_fiyat:,.2f}`\n"
            f"📌 *NET KARAR:* `{tavsiye}`\n"
            f"----------------------------------\n"
            f"📈 *Trend Trendi:* `{trend}`\n"
            f"⚡ *EMA Kesişimi:* `{'EMA9 > EMA21 (Pozitif)' if trend_pozitif else 'EMA9 < EMA21 (Negatif)'}`\n"
            f"📊 *RSI (14):* `{rsi_deger:.1f} ({rsi_durum})`\n"
            f"📉 *MACD:* `{'Pozitif / Güçlü' if macd_val > macd_sig else 'Negatif / Zayıf'}`\n"
            f"📐 *Bollinger:* `Üst: {bb_upper:,.2f} | Alt: {bb_lower:,.2f}`\n"
            f"⚖️ *Risk Değerlendirmesi:* `{risk}`\n"
            f"🕒 *Zaman:* `{su_anki_zaman}`"
        )
        return rapor
    except Exception as e:
        return f"⚠️ Analiz hatası: `{str(e)}`"

def tum_piyasa_analizi_gonder():
    bist, abd, avrupa, etf, fonlar, kriptolar = piyasa_listelerini_getir()
    
    kategoriler = [
        ("🇹🇷 TÜM PİYASA - DİKKAT ÇEKEN YERLİ HİSSELER", bist),
        ("fond TÜM PİYASA - DİKKAT ÇEKEN YERLİ FONLAR", fonlar),
        ("🪙 TÜM PİYASA - DİKKAT ÇEKEN KRİPTOLAR", kriptolar),
        ("🇺🇸 TÜM PİYASA - DİKKAT ÇEKEN ABD HİSSELERİ", abd),
        ("🇪🇺 TÜM PİYASA - DİKKAT ÇEKEN AVRUPA HİSSELERİ", avrupa),
        ("📊 TÜM PİYASA - DİKKAT ÇEKEN ETF'LER", etf)
    ]
    
    telegram_mesaj_gonder("🔎 *Tüm Piyasalar taranıyor, dikkat çeken varlıklar derleniyor...*")
    
    for baslik, liste in kategoriler:
        secilenler = []
        for kod in liste:
            try:
                df = yf.download(kod, period="1mo", interval="1d", progress=False)
                if df.empty or len(df) < 10:
                    continue
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = teknik_indikatorleri_hesapla(df)
                
                fiyat = float(df['Close'].iloc[-1])
                rsi = float(df['RSI'].iloc[-1])
                degisim = ((float(df['Close'].iloc[-1]) - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2])) * 100
                
                if rsi > 60 or rsi < 40 or abs(degisim) > 1.5:
                    temiz_ad = ISIM_SOZLUGU.get(kod, kod.replace(".IS", "").replace("-USD", ""))
                    durum_ikonu = "🔥" if abs(degisim) > 3 else ("🟢" if rsi > 50 else "💡")
                    secilenler.append(f"{durum_ikonu} `{temiz_ad}` | Fiyat: {fiyat:,.2f} | Günlük: %{degisim:+.2f} | RSI: {rsi:.1f}")
                    if len(secilenler) >= 3:
                        break
            except:
                continue
                
        if secilenler:
            mesaj = f"*{baslik}*\n\n" + "\n".join(secilenler)
            telegram_mesaj_gonder(mesaj)
            time.sleep(1)

def komutlari_kontrol_et():
    global last_update_id
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=1"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("ok"):
            for result in data.get("result", []):
                last_update_id = result["update_id"]
                message = result.get("message", {})
                chat_id = str(message.get("chat", {}).get("id"))
                
                if chat_id != TELEGRAM_CHAT_ID:
                    continue
                    
                text = message.get("text", "").strip()
                text_upper = text.upper()
                
                # TÜM PİYASA ANALİZİ KOMUTU
                if "TÜM PİYASA ANALİZİ" in text_upper or text_upper in ["DIKKAT", "DİKKAT", "ÖZET", "OZET"]:
                    tum_piyasa_analizi_gonder()
                
                # EVRENSEL ANALİZ KOMUTU (Küçük/Büyük Harf Bağımsız: analiz, Analiz, ANALİZ, /analiz vb.)
                elif text_upper.startswith("ANALİZ") or text_upper.startswith("ANALIZ") or text_upper.startswith("/ANALIZ"):
                    parcalar = text.split()
                    if len(parcalar) > 1:
                        kod = parcalar[1]
                        telegram_mesaj_gonder(f"⏳ `{kod.upper()}` için detaylı analiz hesaplanıyor...")
                        telegram_mesaj_gonder(evrensel_analiz_et(kod))
                    else:
                        telegram_mesaj_gonder("⚠️ Lütfen bir varlık kodu belirtin.\nÖrnek: `analiz thyao`, `Analiz eth`, `ANALİZ mac`, `analiz aapl`")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    print("Bot tam entegre evrensel analiz moduyla aktif!")
    telegram_mesaj_gonder(
        "🤖 *Bot Güncellendi (Küçük/Büyük Harf Duyarsız Analiz)* \n\n"
        "Artık ister büyük harfle (`ANALİZ THYAO`), ister küçük harfle (`analiz eth`) yaz; sistem komutunu anında kapıp analiz edecektir!\n\n"
        "📌 *Örnek Kullanımlar:*\n"
        "🔹 `analiz thyao` / `ANALİZ THYAO`\n"
        "🔹 `analiz eth` / `ANALİZ ETH`\n"
        "🔹 `analiz mac` (Yerli Fon)\n"
        "🔹 `analiz aapl` (ABD Hissesi)\n"
        "🔹 `Tüm Piyasa Analizi` (Tüm kategorilerdeki gözde varlıkları listeler)"
    )
    
    while True:
        komutlari_kontrol_et()
        time.sleep(10)
