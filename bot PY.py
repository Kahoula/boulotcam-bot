import requests
from bs4 import BeautifulSoup
import schedule
import time
import asyncio
import feedparser
from telegram import Bot

TOKEN = "8946796047:AAFDUkZhoPd639OajwQyzYFinl6DrPBCwbo"
CANAL_ID = "@BoulotCam"

bot = Bot(token=TOKEN)
vus = set()
H = {"User-Agent": "Mozilla/5.0"}

def scrap(url, base, nom):
    offres = []
    try:
        r = requests.get(url, headers=H, timeout=15)
        s = BeautifulSoup(r.text, "html.parser")
        for i in s.find_all(["article", "li"])[:8]:
            t = i.find(["h2", "h3", "h4", "a"])
            l = i.find("a", href=True)
            if t and l:
                ti = t.get_text(strip=True)[:200]
                li = l["href"]
                if not li.startswith("http"):
                    li = base + li
                if len(ti) > 10:
                    offres.append({"t": ti, "l": li, "s": nom})
    except Exception as e:
        print(f"{nom}: {e}")
    return offres

def scrap_rss(url, nom):
    offres = []
    try:
        feed = feedparser.parse(url)
        for e in feed.entries[:5]:
            ti = e.get("title", "")[:200]
            li = e.get("link", "")
            if len(ti) > 10 and li:
                offres.append({"t": ti, "l": li, "s": nom})
    except Exception as e:
        print(f"RSS {nom}: {e}")
    return offres

async def send():
    print("Scraping toutes les sources...")
    all = []
    all += scrap("http://www.fne.cm/offres-demploi/", "http://www.fne.cm", "FNE Cameroun")
    all += scrap("https://www.emploi.cm/offres-emploi", "https://www.emploi.cm", "Emploi.cm")
    all += scrap("https://www.progresscm.com/offres-emploi", "https://www.progresscm.com", "ProgressCM")
    all += scrap("https://reliefweb.int/jobs?country=237", "https://reliefweb.int", "ReliefWeb ONG")
    all += scrap("https://unjobs.org/duty_stations/cameroon", "https://unjobs.org", "ONU Jobs")
    all += scrap("https://www.devex.com/jobs/search?country_id=43", "https://www.devex.com", "Devex ONG")
    all += scrap_rss("https://reliefweb.int/jobs/rss.xml?country=CM", "ReliefWeb RSS")
    print(f"{len(all)} offres trouvees.")
    n = 0
    for o in all:
        k = o["t"][:80]
        if k not in vus:
            vus.add(k)
            msg = (
                f"NOUVELLE OFFRE D'EMPLOI\n\n"
                f"{o['t']}\n\n"
                f"Postuler : {o['l']}\n\n"
                f"Source : {o['s']}\n\n"
                f"BoulotCam — L'emploi qui travaille pour toi\n"
                f"Aucune offre serieuse ne demande de l'argent avant l'embauche."
            )
            try:
                await bot.send_message(chat_id=CANAL_ID, text=msg)
                n += 1
                await asyncio.sleep(4)
            except Exception as e:
                print(f"Erreur envoi: {e}")
    print(f"{n} offre(s) envoyee(s).")

async def rappel():
    msg = (
        "RAPPEL SECURITE — BoulotCam\n\n"
        "ATTENTION AUX ARNAQUES :\n"
        "- Aucune offre serieuse ne demande de l'argent avant l'embauche\n"
        "- BoulotCam ne vous contacte JAMAIS en prive\n"
        "- Ne payez jamais de frais de dossier\n"
        "- Mefiez-vous des numeros inconnus\n\n"
        "BoulotCam — L'emploi qui travaille pour toi"
    )
    try:
        await bot.send_message(chat_id=CANAL_ID, text=msg)
        print("Rappel envoye.")
    except Exception as e:
        print(f"Erreur rappel: {e}")

def job():
    asyncio.run(send())

def job_rappel():
    asyncio.run(rappel())

if __name__ == "__main__":
    print("=" * 40)
    print("BoulotCam Bot demarre...")
    print(f"Canal : {CANAL_ID}")
    print("Sources : FNE, Emploi.cm, ProgressCM,")
    print("          ReliefWeb, ONU Jobs, Devex")
    print("Scan toutes les 10 minutes.")
    print("Rappel anti-arnaque toutes les 48h.")
    print("=" * 40)
    job()
    schedule.every(10).minutes.do(job)
    schedule.every(48).hours.do(job_rappel)
    while True:
        schedule.run_pending()
        time.sleep(30)
