import os
import time
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone

TELEGRAM_BOT_TOKEN = "8616876708:AAEJ7eAubBOcW4VW7EO7Rixpx-qnevZS1bU"
TELEGRAM_CHAT_ID = "906997340"

ISIM_SOZLUGU = {
    "AAPL": "Apple Inc. (ABD)", "MSFT": "Microsoft Corp. (ABD)", "NVDA": "NVIDIA Corp. (ABD)",
    "TSLA": "Tesla Inc. (ABD)", "AMZN": "Amazon.com (ABD)", "GOOGL": "Alphabet / Google (ABD)",
    "META": "Meta Platforms (ABD)", "NFLX": "Netflix Inc. (ABD)", "AMD": "AMD (ABD)",
    "INTC": "Intel Corp. (ABD)", "PLTR": "Palantir Tech (ABD)", "COIN": "Coinbase Global (ABD)",
    "PYPL": "PayPal Holdings (ABD)", "BA": "Boeing Co. (ABD)", "DIS": "Walt Disney (ABD)",
    "NKE": "NIKE Inc. (ABD)", "JPM": "JPMorgan Chase (ABD)", "V": "Visa Inc. (ABD)",
    "WMT": "Walmart Inc. (ABD)", "SPY": "SPDR S&P 500 ETF (ABD)", "QQQ": "Invesco QQQ Trust (ABD)",
    "VOO": "Vanguard S&P 500 ETF", "ARKK": "ARK Innovation ETF", "GLD": "SPDR Gold Shares (Altın ETF)",
    "SLV": "iShares Silver Trust (Gümüş ETF)", "TLT": "iShares 20+ Year Treasury Bond ETF",
    "SAP.DE": "SAP SE (Almanya - DAX)", "SIE.DE": "Siemens AG (Almanya - DAX)", 
    "ALV.DE": "Allianz SE (Almanya - DAX)", "AIR.PA": "Airbus SE (Fransa - CAC)", 
    "MC.PA": "LVMH Moët Hennessy (Fransa - CAC)", "TTE.PA": "TotalEnergies SE (Fransa - CAC)", 
    "OR.PA": "L'Oréal S.A. (Fransa - L'Oreal)", "AZN.L": "AstraZeneca PLC (İngiltere - FTSE)", 
    "SHEL.L": "Shell plc (İngiltere - FTSE)", "HSBA.L": "HSBC Holdings (İngiltere - FTSE)"
}

last_update_id = 0

def get_turkey_time():
    tr_tz = timezone(timedelta(hours=3))
    return datetime.now(tr_tz)

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
    etf_listesi = [
        "SPY", "QQQ", "VOO", "ARKK", "GLD", "SLV", "TLT"
    ]
    return bist_hisseleri, abd_hisseleri, avrupa_hisseleri, etf_listesi

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
    # Kullanıcının yazdığı kodu temizle
    code = hisse_kodu.upper().strip()
    
    # 1. Eğer doğrudan sözlükte varsa veya içinde nokta geçiyorsa (örn: OR.PA, SAP.DE, THYAO.IS) doğrudan dene
    adaylar = [code]
    if not "." in code:
        adaylar = [code + ".IS", code] # Önce BIST uzantısı (.IS) dener, olmazsa saf kodu dener
        
    for aday in adaylar:
        try:
            df_test = yf.download(aday, period="5d", progress=False)
            if not df_test.empty and len(df_test) > 0:
                return aday
        except:
            continue
    return code # Hiçbiri olmazsa orijinali döndürür

def evrensel_analiz_et(hisse_kodu):
    symbol = evrensel_hisse_bul(hisse_kodu)

    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if df.empty or len(df) < 30:
            return f"❌ *{hisse_kodu}* için yeterli veri bulunamadı. Lütfen sembolü kontrol edin (Örn: `THYAO`, `GARAN`, `AAPL`)."
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = teknik_indikatorleri_hesapla(df)
        
        son_fiyat = float(df['Close'].iloc[-1])
        rsi_deger = float(df['RSI'].iloc[-1])
        dunku_ema9 = float(df['EMA9'].iloc[-2])
        bugunku_ema9 = float(df['EMA9'].iloc[-1])
        dunku_ema21 = float(df['EMA21'].iloc[-2])
        bugunku_ema21 = float(df['EMA21'].iloc[-1])

        macd_val = float(df['MACD'].iloc[-1])
        macd_sig = float(df['MACD_Signal'].iloc[-1])
        bb_upper = float(df['BB_Upper'].iloc[-1])
        bb_lower = float(df['BB_Lower'].iloc[-1])
        
        temiz_isim = ISIM_SOZLUGU.get(symbol, symbol)
        su_anki_zaman = get_turkey_time().strftime('%d.%m.%Y %H:%M')

        # Trend durumu
        trend_pozitif = bugunku_ema9 > bugunku_ema21
        trend = "Yükseliş (Boğa) Trendi 🟢" if trend_pozitif else "Düşüş (Ayı) Trendi 🔴"

        # RSI Durumu
        if rsi_deger > 70:
            rsi_durum = "Aşırı Alım Bölgesinde ⚠️"
        elif rsi_deger < 30:
            rsi_durum = "Aşırı Satım Bölgesinde (Fırsat) 💡"
        else:
            rsi_durum = "Normal Bantta 📊"

        # NET KARAR (AL / SAT / TUT / UZAK DUR) MEKANİZMASI
        if trend_pozitif and rsi_deger <= 65 and macd_val > macd_sig:
            tavsiye = "GÜÇLÜ AL 🟢 (Yükseliş Trendi & Destekli)"
            risk = "Düşük / Orta"
        elif trend_pozitif and rsi_deger > 70:
            tavsiye = "TUT / KÂR AL 🟡 (Aşırı Alım Sınırında, Dikkatli Ol)"
            risk = "Orta - Yüksek"
        elif not trend_pozitif and rsi_deger < 35:
            tavsiye = "TUT / İZLE 🟡 (Dip Arayışı / Destek Bölgesi)"
            risk = "Orta"
        elif not trend_pozitif and rsi_deger >= 35:
            tavsiye = "SAT / UZAK DUR 🔴 (Düşüş Trendi Baskın)"
            risk = "Yüksek"
        else:
            tavsiye = "TUT / BEKLE ⚖️ (Yatay veya Kararsız Seyir)"
            risk = "Dengeli / Orta"

        rapor = (
            f"🎯 *DETAYLI VARLIK ANALİZİ VE KARAR*\n\n"
            f"🏢 *Varlık:* `{temiz_isim}`\n"
            f"💰 *Güncel Fiyat:* `{son_fiyat:.2f}`\n"
            f"📌 *NET KARAR:* `{tavsiye}`\n"
            f"----------------------------------\n"
            f"📈 *Trend Durumu:* `{trend}`\n"
            f"⚡ *EMA Kesişimi:* `{'EMA9 > EMA21 (Pozitif)' if trend_pozitif else 'EMA9 < EMA21 (Negatif)'}`\n"
            f"📊 *RSI (14):* `{rsi_deger:.1f} ({rsi_durum})`\n"
            f"📉 *MACD:* `{'Pozitif / Güçlü' if macd_val > macd_sig else 'Negatif / Zayıf'}`\n"
            f"📐 *Bollinger Bantları:* `Üst: {bb_upper:.2f} | Alt: {bb_lower:.2f}`\n"
            f"⚖️ *Risk Değerlendirmesi:* `{risk}`\n"
            f"🕒 *Zaman:* `{su_anki_zaman}`"
        )
        return rapor
    except Exception as e:
        return f"⚠️ Analiz hatası: `{str(e)}`. Lütfen geçerli bir borsa kodu girdiğinizden emin olun."

def etf_fon_tara_ve_gonder(etf_listesi):
    bulunan = 0
    for etf in etf_listesi:
        try:
            df = yf.download(etf, period="2mo", interval="1d", progress=False)
            if df.empty or len(df) < 30:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = teknik_indikatorleri_hesapla(df)
            son_fiyat = float(df['Close'].iloc[-1])
            rsi_deger = float(df['RSI'].iloc[-1])
            dunku_ema9 = float(df['EMA9'].iloc[-2])
            bugunku_ema9 = float(df['EMA9'].iloc[-1])
            dunku_ema21 = float(df['EMA21'].iloc[-2])
            bugunku_ema21 = float(df['EMA21'].iloc[-1])
            
            temiz_isim = ISIM_SOZLUGU.get(etf, etf)
            su_anki_zaman = get_turkey_time().strftime('%d.%m.%Y %H:%M')

            if dunku_ema9 <= dunku_ema21 and bugunku_ema9 > bugunku_ema21:
                mesaj = (
                    f"🟢 *ETF / FON - AL SİNYALİ*\n\n"
                    f"📦 *Fon/ETF:* `{temiz_isim}`\n"
                    f"💰 *Fiyat:* `{son_fiyat:.2f} $`\n"
                    f"📊 *RSI:* `{rsi_deger:.1f}`\n"
                    f"🕒 *Zaman:* `{su_anki_zaman}`"
                )
                telegram_mesaj_gonder(mesaj)
                time.sleep(15)
                bulunan += 1
            elif dunku_ema9 >= dunku_ema21 and bugunku_ema9 < bugunku_ema21:
                mesaj = (
                    f"🔴 *ETF / FON - SAT SİNYALİ*\n\n"
                    f"📦 *Fon/ETF:* `{temiz_isim}`\n"
                    f"💰 *Fiyat:* `{son_fiyat:.2f} $`\n"
                    f"📊 *RSI:* `{rsi_deger:.1f}`\n"
                    f"🕒 *Zaman:* `{su_anki_zaman}`"
                )
                telegram_mesaj_gonder(mesaj)
                time.sleep(15)
                bulunan += 1
        except Exception:
            pass
    return bulunan

def hisse_tara_ve_gonder(hisse_listesi, kategori_adi, para_birimi):
    bulunan = 0
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
            dunku_ema9 = float(df['EMA9'].iloc[-2])
            bugunku_ema9 = float(df['EMA9'].iloc[-1])
            dunku_ema21 = float(df['EMA21'].iloc[-2])
            bugunku_ema21 = float(df['EMA21'].iloc[-1])
            
            temiz_isim = ISIM_SOZLUGU.get(hisse, hisse.replace(".IS", ""))
            su_anki_zaman = get_turkey_time().strftime('%d.%m.%Y %H:%M')

            if dunku_ema9 <= dunku_ema21 and bugunku_ema9 > bugunku_ema21:
                mesaj = (
                    f"🟢 *{kategori_adi} - AL SİNYALİ*\n\n"
                    f"🏢 *Varlık:* `{temiz_isim}`\n"
                    f"💰 *Fiyat:* `{son_fiyat:.2f} {para_birimi}`\n"
                    f"📊 *RSI:* `{rsi_deger:.1f}`\n"
                    f"🕒 *Zaman:* `{su_anki_zaman}`"
                )
                telegram_mesaj_gonder(mesaj)
                time.sleep(15)
                bulunan += 1
            elif dunku_ema9 >= dunku_ema21 and bugunku_ema9 < bugunku_ema21:
                mesaj = (
                    f"🔴 *{kategori_adi} - SAT SİNYALİ*\n\n"
                    f"🏢 *Varlık:* `{temiz_isim}`\n"
                    f"💰 *Fiyat:* `{son_fiyat:.2f} {para_birimi}`\n"
                    f"📊 *RSI:* `{rsi_deger:.1f}`\n"
                    f"🕒 *Zaman:* `{su_anki_zaman}`"
                )
                telegram_mesaj_gonder(mesaj)
                time.sleep(15)
                bulunan += 1
        except Exception:
            pass
    return bulunan

def komutlari_kontrol_et():
    global last_update_id
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=1"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("ok"):
            bist, abd, avrupa, etf = piyasa_listelerini_getir()
            for result in data.get("result", []):
                last_update_id = result["update_id"]
                message = result.get("message", {})
                chat_id = str(message.get("chat", {}).get("id"))
                
                if chat_id != TELEGRAM_CHAT_ID:
                    continue
                    
                text = message.get("text", "").strip()
                text_upper = text.upper()
                
                if text_upper.startswith("ANALİZ") or text_upper.startswith("/ANALIZ"):
                    parcalar = text.split()
                    if len(parcalar) > 1:
                        hisse_kodu = parcalar[1]
                        telegram_mesaj_gonder(f"⏳ `{hisse_kodu.upper()}` için evrensel teknik analiz hesaplanıyor...")
                        analiz_sonucu = evrensel_analiz_et(hisse_kodu)
                        telegram_mesaj_gonder(analiz_sonucu)
                    else:
                        telegram_mesaj_gonder("⚠️ Lütfen kod belirtin. Örnek: `ANALİZ THYAO`, `ANALİZ GARAN`, `ANALİZ AAPL`")
                
                elif text_upper.startswith("FON") or text_upper.startswith("/FON"):
                    parcalar = text.split()
                    if len(parcalar) > 1:
                        fon_kodu = parcalar[1]
                        telegram_mesaj_gonder(f"⏳ `{fon_kodu.upper()}` fonu/ETF'i analiz ediliyor...")
                        analiz_sonucu = evrensel_analiz_et(fon_kodu)
                        telegram_mesaj_gonder(analiz_sonucu)
                    else:
                        telegram_mesaj_gonder("⚠️ Örnek: `FON QQQ` veya `FON SPY`")
                
                elif text_upper in ["/BIST", "BIST"]:
                    telegram_mesaj_gonder("🔍 *BIST 100* taraması başlatıldı...")
                    adet = hisse_tara_ve_gonder(bist, "BIST 100", "TL")
                    telegram_mesaj_gonder(f"✅ BIST bitti. Bulunan sinyal: {adet}")
                    
                elif text_upper in ["/ABD", "ABD"]:
                    telegram_mesaj_gonder("🔍 *ABD Borsa* taraması başlatıldı...")
                    adet = hisse_tara_ve_gonder(abd, "ABD BORSALARI", "$")
                    telegram_mesaj_gonder(f"✅ ABD bitti. Bulunan sinyal: {adet}")
                    
                elif text_upper in ["/AVRUPA", "AVRUPA"]:
                    telegram_mesaj_gonder("🔍 *Avrupa Borsa* taraması başlatıldı...")
                    adet = hisse_tara_ve_gonder(avrupa, "AVRUPA BORSALARI", "€ / £")
                    telegram_mesaj_gonder(f"✅ Avrupa bitti. Bulunan sinyal: {adet}")

                elif text_upper in ["/ETF", "ETF", "FONLER"]:
                    telegram_mesaj_gonder("🔍 *ETF / Fonlar* taranıyor...")
                    adet = etf_fon_tara_ve_gonder(etf)
                    telegram_mesaj_gonder(f"✅ ETF taraması bitti. Bulunan sinyal: {adet}")
                    
                elif text_upper in ["/TUMU", "TÜMÜ", "TUM"]:
                    telegram_mesaj_gonder("🔍 Tüm piyasalar taranıyor...")
                    s1 = hisse_tara_ve_gonder(bist, "BIST 100", "TL")
                    s2 = hisse_tara_ve_gonder(abd, "ABD BORSALARI", "$")
                    s3 = hisse_tara_ve_gonder(avrupa, "AVRUPA BORSALARI", "€ / £")
                    s4 = etf_fon_tara_ve_gonder(etf)
                    telegram_mesaj_gonder(f"✅ Taramalar bitti. Toplam sinyal: {s1 + s2 + s3 + s4}")
    except Exception as e:
        print(f"Komut okuma hatası: {e}")

if __name__ == "__main__":
    print("Bot evrensel analiz moduyla aktif!")
    telegram_mesaj_gonder(
        "🤖 *Bot Güncellendi (Evrensel Arama & Net Karar Eklendi)* \n\n"
        "Artık dünyanın veya BIST'in **istediğin herhangi bir hisse kodunu** yazarak analiz edebilirsin!\n\n"
        "📌 *Örnek Komutlar:*\n"
        "🔹 `ANALİZ THYAO`\n"
        "🔹 `ANALİZ GARAN`\n"
        "🔹 `ANALİZ KCHOL`\n"
        "🔹 `ANALİZ AAPL`\n"
        "🔹 `BIST` / `ABD` / `ETF`"
    )
    
    while True:
        komutlari_kontrol_et()
        time.sleep(10)
