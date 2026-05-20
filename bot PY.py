import requests
from bs4 import BeautifulSoup
import schedule
import time
import asyncio
import feedparser
from telegram import Bot
from datetime import datetime, timedelta

TOKEN = "8946796047:AAFrlWEkzdB7a8dMQXE6h2LzOuTVt0tFkzE"
CANAL_ID = "@BoulotCam"

bot = Bot(token=TOKEN)
vus = set()
H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def formater_offre(titre, entreprise, ville, date_limite, lien, source):
    ville_str = f"📍 Lieu : {ville}\n" if ville and ville.strip() else ""
    date_str = f"📅 Limite : {date_limite}\n" if date_limite and date_limite.strip() else ""
    entreprise_str = f"🏢 Entreprise : {entreprise}\n" if entreprise and entreprise.strip() else ""
    return (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💼 NOUVELLE OFFRE D'EMPLOI\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 {titre}\n\n"
        f"{entreprise_str}"
        f"{ville_str}"
        f"{date_str}\n"
        f"🔗 Postuler directement : {lien}\n\n"
        f"📡 Source : {source}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"BoulotCam — L'emploi qui travaille pour toi 🇨🇲\n"
        f"⚠️ Aucune offre serieuse ne demande de l'argent avant l'embauche."
    )

# ============================================================
# EMPLOI.CM
# ============================================================
def scraper_emploi_cm():
    offres = []
    try:
        url = "https://www.emploi.cm/offres-emploi"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all(["div", "article"], class_=lambda x: x and any(k in str(x).lower() for k in ["job", "offre", "views-row", "card"]))[:10]
        for item in items:
            try:
                titre_el = item.find(["h2", "h3", "h4"])
                lien_el = item.find("a", href=True)
                ville_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["ville", "city", "location", "lieu"]))
                entreprise_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["entreprise", "company", "employer", "societe"]))
                date_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["date", "expire", "deadline", "limite"]))
                if titre_el and lien_el:
                    titre = titre_el.get_text(strip=True)[:200]
                    lien = lien_el["href"]
                    if not lien.startswith("http"):
                        lien = "https://www.emploi.cm" + lien
                    ville = ville_el.get_text(strip=True) if ville_el else "Cameroun"
                    entreprise = entreprise_el.get_text(strip=True) if entreprise_el else ""
                    date_limite = date_el.get_text(strip=True) if date_el else ""
                    if len(titre) > 10:
                        offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date_limite, "lien": lien, "source": "Emploi.cm"})
            except:
                continue
    except Exception as e:
        print(f"Emploi.cm erreur: {e}")
    return offres

# ============================================================
# JOBINCAMER.COM
# ============================================================
def scraper_jobincamer():
    offres = []
    try:
        url = "https://www.jobincamer.com/offres-emploi"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all(["div", "article", "li"], class_=lambda x: x and any(k in str(x).lower() for k in ["job", "offre", "item", "card", "post"]))[:10]
        for item in items:
            try:
                titre_el = item.find(["h2", "h3", "h4", "a"])
                lien_el = item.find("a", href=True)
                ville_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["ville", "city", "location", "lieu"]))
                entreprise_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["entreprise", "company", "employer"]))
                date_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["date", "expire", "deadline"]))
                if titre_el and lien_el:
                    titre = titre_el.get_text(strip=True)[:200]
                    lien = lien_el["href"]
                    if not lien.startswith("http"):
                        lien = "https://www.jobincamer.com" + lien
                    ville = ville_el.get_text(strip=True) if ville_el else "Cameroun"
                    entreprise = entreprise_el.get_text(strip=True) if entreprise_el else ""
                    date_limite = date_el.get_text(strip=True) if date_el else ""
                    if len(titre) > 10:
                        offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date_limite, "lien": lien, "source": "JobInCamer"})
            except:
                continue
    except Exception as e:
        print(f"JobInCamer erreur: {e}")
    return offres

# ============================================================
# MINAJOBS.NET CAMEROUN
# ============================================================
def scraper_minajobs():
    offres = []
    try:
        url = "https://cameroun.minajobs.net/offres-emploi"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all(["div", "article", "li"], class_=lambda x: x and any(k in str(x).lower() for k in ["job", "offre", "item", "card"]))[:10]
        for item in items:
            try:
                titre_el = item.find(["h2", "h3", "h4", "a"])
                lien_el = item.find("a", href=True)
                ville_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["ville", "city", "location", "lieu", "region"]))
                entreprise_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["entreprise", "company", "employer", "organis"]))
                date_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["date", "expire", "deadline", "limite"]))
                if titre_el and lien_el:
                    titre = titre_el.get_text(strip=True)[:200]
                    lien = lien_el["href"]
                    if not lien.startswith("http"):
                        lien = "https://cameroun.minajobs.net" + lien
                    ville = ville_el.get_text(strip=True) if ville_el else "Cameroun"
                    entreprise = entreprise_el.get_text(strip=True) if entreprise_el else ""
                    date_limite = date_el.get_text(strip=True) if date_el else ""
                    if len(titre) > 10:
                        offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date_limite, "lien": lien, "source": "MinaJobs Cameroun"})
            except:
                continue
    except Exception as e:
        print(f"MinaJobs erreur: {e}")
    return offres

# ============================================================
# FNE CAMEROUN
# ============================================================
def scraper_fne():
    offres = []
    try:
        url = "https://fnecm.org/index.php/fr/chercheurs-demploi-45"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all(["div", "article", "li", "tr"])[:15]
        for item in items:
            try:
                titre_el = item.find(["h2", "h3", "h4", "a", "td"])
                lien_el = item.find("a", href=True)
                if titre_el and lien_el:
                    titre = titre_el.get_text(strip=True)[:200]
                    lien = lien_el["href"]
                    if not lien.startswith("http"):
                        lien = "https://fnecm.org" + lien
                    if len(titre) > 10 and "emploi" not in titre.lower()[:20]:
                        offres.append({"titre": titre, "entreprise": "FNE Cameroun", "ville": "Cameroun", "date": "", "lien": lien, "source": "FNE Officiel"})
            except:
                continue
    except Exception as e:
        print(f"FNE erreur: {e}")
    return offres

# ============================================================
# JOBARTIS CAMEROUN
# ============================================================
def scraper_jobartis():
    offres = []
    try:
        url = "https://www.jobartiscameroun.com/emplois/duree-indeterminee"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all(["div", "article", "li"], class_=lambda x: x and any(k in str(x).lower() for k in ["job", "offre", "item", "card", "listing"]))[:10]
        for item in items:
            try:
                titre_el = item.find(["h2", "h3", "h4", "a"])
                lien_el = item.find("a", href=True)
                ville_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["ville", "city", "location", "lieu"]))
                entreprise_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["entreprise", "company", "employer"]))
                date_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["date", "expire", "deadline"]))
                if titre_el and lien_el:
                    titre = titre_el.get_text(strip=True)[:200]
                    lien = lien_el["href"]
                    if not lien.startswith("http"):
                        lien = "https://www.jobartiscameroun.com" + lien
                    ville = ville_el.get_text(strip=True) if ville_el else "Cameroun"
                    entreprise = entreprise_el.get_text(strip=True) if entreprise_el else ""
                    date_limite = date_el.get_text(strip=True) if date_el else ""
                    if len(titre) > 10:
                        offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date_limite, "lien": lien, "source": "JobArtis Cameroun"})
            except:
                continue
    except Exception as e:
        print(f"JobArtis erreur: {e}")
    return offres

# ============================================================
# TECTRA.CM
# ============================================================
def scraper_tectra():
    offres = []
    try:
        url = "https://tectra.cm/offres-emploi"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all(["div", "article", "li"], class_=lambda x: x and any(k in str(x).lower() for k in ["job", "offre", "item", "card", "post"]))[:10]
        for item in items:
            try:
                titre_el = item.find(["h2", "h3", "h4", "a"])
                lien_el = item.find("a", href=True)
                ville_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["ville", "city", "location", "lieu"]))
                entreprise_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["entreprise", "company", "client"]))
                date_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["date", "expire", "deadline", "limite"]))
                if titre_el and lien_el:
                    titre = titre_el.get_text(strip=True)[:200]
                    lien = lien_el["href"]
                    if not lien.startswith("http"):
                        lien = "https://tectra.cm" + lien
                    ville = ville_el.get_text(strip=True) if ville_el else "Cameroun"
                    entreprise = entreprise_el.get_text(strip=True) if entreprise_el else "Tectra"
                    date_limite = date_el.get_text(strip=True) if date_el else ""
                    if len(titre) > 10:
                        offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date_limite, "lien": lien, "source": "Tectra.cm"})
            except:
                continue
    except Exception as e:
        print(f"Tectra erreur: {e}")
    return offres

# ============================================================
# MICHAEL PAGE AFRICA — CAMEROUN
# ============================================================
def scraper_michaelpage():
    offres = []
    try:
        url = "https://www.michaelpageafrica.com/fr/jobs/cameroon"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all(["div", "article", "li"], class_=lambda x: x and any(k in str(x).lower() for k in ["job", "offre", "item", "card", "result"]))[:10]
        for item in items:
            try:
                titre_el = item.find(["h2", "h3", "h4", "a"])
                lien_el = item.find("a", href=True)
                ville_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["ville", "city", "location", "lieu"]))
                entreprise_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["entreprise", "company", "client", "employer"]))
                date_el = item.find(class_=lambda x: x and any(k in str(x).lower() for k in ["date", "posted", "publie"]))
                if titre_el and lien_el:
                    titre = titre_el.get_text(strip=True)[:200]
                    lien = lien_el["href"]
                    if not lien.startswith("http"):
                        lien = "https://www.michaelpageafrica.com" + lien
                    ville = ville_el.get_text(strip=True) if ville_el else "Cameroun"
                    entreprise = entreprise_el.get_text(strip=True) if entreprise_el else ""
                    date_limite = date_el.get_text(strip=True) if date_el else ""
                    if len(titre) > 10:
                        offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date_limite, "lien": lien, "source": "Michael Page Africa"})
            except:
                continue
    except Exception as e:
        print(f"MichaelPage erreur: {e}")
    return offres

# ============================================================
# RELIEFWEB RSS — ONG ET HUMANITAIRE
# ============================================================
def scraper_reliefweb_rss():
    offres = []
    try:
        feed = feedparser.parse("https://reliefweb.int/jobs/rss.xml?country=CM")
        for e in feed.entries[:10]:
            titre = e.get("title", "")[:200]
            lien = e.get("link", "")
            ville = "Cameroun"
            entreprise = e.get("source", {}).get("title", "") if hasattr(e, "source") else ""
            date_limite = ""
            if titre and lien and len(titre) > 10:
                offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date_limite, "lien": lien, "source": "ReliefWeb ONG"})
    except Exception as e:
        print(f"ReliefWeb RSS erreur: {e}")
    return offres

# ============================================================
# UN JOBS — NATIONS UNIES CAMEROUN
# ============================================================
def scraper_unjobs():
    offres = []
    try:
        url = "https://unjobs.org/duty_stations/cameroon"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("div", class_=lambda x: x and "job" in str(x).lower())[:10]
        if not items:
            items = soup.find_all("li")[:10]
        for item in items:
            try:
                titre_el = item.find(["h2", "h3", "a"])
                lien_el = item.find("a", href=True)
                if titre_el and lien_el:
                    titre = titre_el.get_text(strip=True)[:200]
                    lien = lien_el["href"]
                    if not lien.startswith("http"):
                        lien = "https://unjobs.org" + lien
                    if len(titre) > 10:
                        offres.append({"titre": titre, "entreprise": "Nations Unies", "ville": "Cameroun", "date": "", "lien": lien, "source": "ONU Jobs"})
            except:
                continue
    except Exception as e:
        print(f"UNJobs erreur: {e}")
    return offres

# ============================================================
# ENVOI TELEGRAM
# ============================================================
async def envoyer_offres():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scraping toutes les sources...")
    toutes = []
    toutes += scraper_emploi_cm()
    toutes += scraper_jobincamer()
    toutes += scraper_minajobs()
    toutes += scraper_fne()
    toutes += scraper_jobartis()
    toutes += scraper_tectra()
    toutes += scraper_michaelpage()
    toutes += scraper_reliefweb_rss()
    toutes += scraper_unjobs()

    print(f"{len(toutes)} offres trouvees au total.")
    n = 0
    for o in toutes:
        cle = o["titre"][:80] + o["lien"][:40]
        if cle not in vus:
            vus.add(cle)
            msg = formater_offre(o["titre"], o["entreprise"], o["ville"], o["date"], o["lien"], o["source"])
            try:
                await bot.send_message(chat_id=CANAL_ID, text=msg)
                n += 1
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Erreur envoi: {e}")
    print(f"{n} nouvelle(s) offre(s) envoyee(s).")

async def rappel():
    msg = (
        "🛡️ RAPPEL SECURITE — BoulotCam\n\n"
        "ATTENTION AUX ARNAQUES :\n"
        "❌ Aucune offre serieuse ne demande de l'argent avant l'embauche\n"
        "❌ BoulotCam ne vous contacte JAMAIS en prive\n"
        "❌ Ne payez jamais de frais de dossier\n"
        "❌ Mefiez-vous des numeros inconnus\n\n"
        "✅ En cas de doute : signalez dans le groupe de discussion\n\n"
        "BoulotCam — L'emploi qui travaille pour toi 🇨🇲"
    )
    try:
        await bot.send_message(chat_id=CANAL_ID, text=msg)
    except Exception as e:
        print(f"Erreur rappel: {e}")

def job():
    asyncio.run(envoyer_offres())

def job_rappel():
    asyncio.run(rappel())

if __name__ == "__main__":
    print("=" * 45)
    print("BoulotCam Bot demarre...")
    print(f"Canal : {CANAL_ID}")
    print("Sources actives :")
    print("  - Emploi.cm")
    print("  - JobInCamer")
    print("  - MinaJobs Cameroun")
    print("  - FNE Officiel")
    print("  - JobArtis Cameroun")
    print("  - Tectra.cm")
    print("  - Michael Page Africa")
    print("  - ReliefWeb ONG (RSS)")
    print("  - ONU Jobs")
    print("Scan toutes les 10 minutes.")
    print("Rappel anti-arnaque toutes les 48h.")
    print("=" * 45)
    job()
    schedule.every(10).minutes.do(job)
    schedule.every(48).hours.do(job_rappel)
    while True:
        schedule.run_pending()
        time.sleep(30)

