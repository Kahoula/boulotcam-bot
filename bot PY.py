import requests
from bs4 import BeautifulSoup
import schedule
import time
import asyncio
import feedparser
from telegram import Bot
from datetime import datetime

TOKEN = "8946796047:AAFrlWEkzdB7a8dMQXE6h2LzOuTVt0tFkzE"
CANAL_ID = "@BoulotCam"

bot = Bot(token=TOKEN)
vus = set()

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def formater(titre, entreprise, ville, date, lien, source):
    e = f"🏢 {entreprise.strip()}\n" if entreprise and len(entreprise.strip()) > 2 else ""
    v = f"📍 {ville.strip()}\n" if ville and len(ville.strip()) > 2 else "📍 Cameroun\n"
    d = f"📅 Limite : {date.strip()}\n" if date and len(date.strip()) > 2 else ""
    return (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💼 NOUVELLE OFFRE\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 {titre.strip()}\n\n"
        f"{e}{v}{d}\n"
        f"🔗 Postuler : {lien}\n\n"
        f"📡 {source}\n\n"
        f"BoulotCam 🇨🇲 — L'emploi qui travaille pour toi\n"
        f"⚠️ Aucune offre serieuse ne demande d'argent avant embauche"
    )

# ================================================================
# EMPLOI.CM — scraping page liste + detail chaque annonce
# ================================================================
def scraper_emploi_cm():
    offres = []
    try:
        for page in range(1, 3):
            url = f"https://www.emploi.cm/offres-emploi?page={page}"
            r = requests.get(url, headers=H, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            liens = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/offre-emploi/" in href or "/offres-emploi/" in href:
                    if not href.startswith("http"):
                        href = "https://www.emploi.cm" + href
                    if href not in liens:
                        liens.append(href)
            for lien in liens[:8]:
                try:
                    r2 = requests.get(lien, headers=H, timeout=10)
                    s2 = BeautifulSoup(r2.text, "html.parser")
                    titre_el = s2.find("h1") or s2.find("h2")
                    titre = titre_el.get_text(strip=True)[:200] if titre_el else ""
                    ville = ""
                    entreprise = ""
                    date = ""
                    for span in s2.find_all(["span", "div", "p", "li"]):
                        txt = span.get_text(strip=True).lower()
                        if any(v in txt for v in ["yaoundé", "douala", "bafoussam", "garoua", "maroua", "bertoua", "ebolowa", "buea", "ngaoundéré", "bamenda", "kumba"]):
                            if not ville:
                                ville = span.get_text(strip=True)[:50]
                        if any(k in txt for k in ["date limite", "date de clôture", "expire", "deadline", "postuler avant"]):
                            if not date:
                                date = span.get_text(strip=True)[:80]
                    entreprise_el = s2.find(class_=lambda x: x and any(k in str(x).lower() for k in ["company", "employer", "entreprise", "societe", "recruteur"]))
                    if entreprise_el:
                        entreprise = entreprise_el.get_text(strip=True)[:100]
                    if titre and len(titre) > 10:
                        cle = titre[:60] + lien[:40]
                        if cle not in vus:
                            vus.add(cle)
                            offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date, "lien": lien, "source": "Emploi.cm"})
                    time.sleep(1)
                except:
                    continue
    except Exception as e:
        print(f"Emploi.cm erreur: {e}")
    return offres

# ================================================================
# JOBINCAMER.COM
# ================================================================
def scraper_jobincamer():
    offres = []
    try:
        for page in range(1, 3):
            url = f"https://www.jobincamer.com/offres-emploi?page={page}"
            r = requests.get(url, headers=H, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            liens = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/offre/" in href or "/emploi/" in href or "/job/" in href:
                    if not href.startswith("http"):
                        href = "https://www.jobincamer.com" + href
                    if href not in liens:
                        liens.append(href)
            for lien in liens[:8]:
                try:
                    r2 = requests.get(lien, headers=H, timeout=10)
                    s2 = BeautifulSoup(r2.text, "html.parser")
                    titre_el = s2.find("h1") or s2.find("h2")
                    titre = titre_el.get_text(strip=True)[:200] if titre_el else ""
                    ville = ""
                    entreprise = ""
                    date = ""
                    for el in s2.find_all(["span", "div", "p", "td", "li"]):
                        txt = el.get_text(strip=True)
                        txt_low = txt.lower()
                        if any(v in txt_low for v in ["yaoundé", "douala", "bafoussam", "garoua", "maroua", "bertoua", "littoral", "centre", "ouest", "nord"]):
                            if not ville and len(txt) < 60:
                                ville = txt
                        if any(k in txt_low for k in ["date limite", "expire", "deadline", "avant le", "postuler avant"]):
                            if not date and len(txt) < 80:
                                date = txt
                        if any(k in txt_low for k in ["entreprise", "société", "recruteur", "employeur", "cabinet"]):
                            if not entreprise and len(txt) < 100:
                                entreprise = txt
                    if titre and len(titre) > 10:
                        cle = titre[:60] + lien[:40]
                        if cle not in vus:
                            vus.add(cle)
                            offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date, "lien": lien, "source": "JobInCamer"})
                    time.sleep(1)
                except:
                    continue
    except Exception as e:
        print(f"JobInCamer erreur: {e}")
    return offres

# ================================================================
# MINAJOBS CAMEROUN
# ================================================================
def scraper_minajobs():
    offres = []
    try:
        url = "https://cameroun.minajobs.net/offres-emploi"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        liens = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/offre" in href or "/emploi" in href or "/job" in href:
                if not href.startswith("http"):
                    href = "https://cameroun.minajobs.net" + href
                if href not in liens and "cameroun.minajobs.net" in href:
                    liens.append(href)
        for lien in liens[:8]:
            try:
                r2 = requests.get(lien, headers=H, timeout=10)
                s2 = BeautifulSoup(r2.text, "html.parser")
                titre_el = s2.find("h1") or s2.find("h2")
                titre = titre_el.get_text(strip=True)[:200] if titre_el else ""
                ville = ""
                entreprise = ""
                date = ""
                for el in s2.find_all(["span", "div", "p", "td", "li"]):
                    txt = el.get_text(strip=True)
                    txt_low = txt.lower()
                    if any(v in txt_low for v in ["yaoundé", "douala", "bafoussam", "garoua", "maroua", "adamaoua", "centre", "littoral", "ouest", "nord", "sud", "est"]):
                        if not ville and len(txt) < 60:
                            ville = txt
                    if any(k in txt_low for k in ["date limite", "expire", "deadline", "avant le"]):
                        if not date and len(txt) < 80:
                            date = txt
                    if any(k in txt_low for k in ["entreprise", "société", "recruteur", "employeur"]):
                        if not entreprise and len(txt) < 100:
                            entreprise = txt
                if titre and len(titre) > 10:
                    cle = titre[:60] + lien[:40]
                    if cle not in vus:
                        vus.add(cle)
                        offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date, "lien": lien, "source": "MinaJobs Cameroun"})
                time.sleep(1)
            except:
                continue
    except Exception as e:
        print(f"MinaJobs erreur: {e}")
    return offres

# ================================================================
# FNE OFFICIEL
# ================================================================
def scraper_fne():
    offres = []
    try:
        url = "https://fnecm.org/index.php/fr/chercheurs-demploi-45"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        liens = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "fnecm.org" in href or href.startswith("/"):
                if not href.startswith("http"):
                    href = "https://fnecm.org" + href
                if href not in liens and href != "https://fnecm.org/index.php/fr/chercheurs-demploi-45":
                    liens.append(href)
        for lien in liens[:6]:
            try:
                r2 = requests.get(lien, headers=H, timeout=10)
                s2 = BeautifulSoup(r2.text, "html.parser")
                titre_el = s2.find("h1") or s2.find("h2")
                titre = titre_el.get_text(strip=True)[:200] if titre_el else ""
                ville = ""
                date = ""
                for el in s2.find_all(["span", "div", "p", "td"]):
                    txt = el.get_text(strip=True)
                    txt_low = txt.lower()
                    if any(v in txt_low for v in ["yaoundé", "douala", "bafoussam", "garoua", "maroua", "bertoua"]):
                        if not ville and len(txt) < 60:
                            ville = txt
                    if any(k in txt_low for k in ["date limite", "expire", "deadline", "avant le"]):
                        if not date and len(txt) < 80:
                            date = txt
                if titre and len(titre) > 10:
                    cle = titre[:60] + lien[:40]
                    if cle not in vus:
                        vus.add(cle)
                        offres.append({"titre": titre, "entreprise": "FNE Cameroun", "ville": ville, "date": date, "lien": lien, "source": "FNE Officiel"})
                time.sleep(1)
            except:
                continue
    except Exception as e:
        print(f"FNE erreur: {e}")
    return offres

# ================================================================
# JOBARTIS CAMEROUN
# ================================================================
def scraper_jobartis():
    offres = []
    try:
        url = "https://www.jobartiscameroun.com/emplois/duree-indeterminee"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        liens = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/emploi-" in href:
                if not href.startswith("http"):
                    href = "https://www.jobartiscameroun.com" + href
                if href not in liens:
                    liens.append(href)
        for lien in liens[:8]:
            try:
                r2 = requests.get(lien, headers=H, timeout=10)
                s2 = BeautifulSoup(r2.text, "html.parser")
                titre_el = s2.find("h1") or s2.find("h2")
                titre = titre_el.get_text(strip=True)[:200] if titre_el else ""
                ville = ""
                entreprise = ""
                date = ""
                for el in s2.find_all(["span", "div", "p", "td", "li"]):
                    txt = el.get_text(strip=True)
                    txt_low = txt.lower()
                    if any(v in txt_low for v in ["douala", "yaoundé", "bafoussam", "garoua", "maroua", "adamaoua", "littoral", "centre", "ouest", "nord", "sud-ouest", "nord-ouest", "est", "sud"]):
                        if not ville and len(txt) < 60:
                            ville = txt
                    if any(k in txt_low for k in ["date limite", "expire", "deadline", "avant le", "postuler avant"]):
                        if not date and len(txt) < 80:
                            date = txt
                    if any(k in txt_low for k in ["entreprise", "société", "recruteur", "employeur", "cabinet", "energy", "sarl", "sa ", "group"]):
                        if not entreprise and len(txt) < 100 and len(txt) > 3:
                            entreprise = txt
                if titre and len(titre) > 10:
                    cle = titre[:60] + lien[:40]
                    if cle not in vus:
                        vus.add(cle)
                        offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date, "lien": lien, "source": "JobArtis Cameroun"})
                time.sleep(1)
            except:
                continue
    except Exception as e:
        print(f"JobArtis erreur: {e}")
    return offres

# ================================================================
# TECTRA — offres sur talent-tectra.com
# ================================================================
def scraper_tectra():
    offres = []
    try:
        url = "https://talent-tectra.com/s3/annonces"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        liens = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/annonce/" in href or "/offre/" in href or "/job/" in href:
                if not href.startswith("http"):
                    href = "https://talent-tectra.com" + href
                if href not in liens:
                    liens.append(href)
        for lien in liens[:6]:
            try:
                r2 = requests.get(lien, headers=H, timeout=10)
                s2 = BeautifulSoup(r2.text, "html.parser")
                titre_el = s2.find("h1") or s2.find("h2")
                titre = titre_el.get_text(strip=True)[:200] if titre_el else ""
                ville = ""
                date = ""
                for el in s2.find_all(["span", "div", "p", "td"]):
                    txt = el.get_text(strip=True)
                    txt_low = txt.lower()
                    if any(v in txt_low for v in ["yaoundé", "douala", "bafoussam", "garoua", "cameroun"]):
                        if not ville and len(txt) < 60:
                            ville = txt
                    if any(k in txt_low for k in ["date limite", "expire", "deadline", "avant le"]):
                        if not date and len(txt) < 80:
                            date = txt
                if titre and len(titre) > 10:
                    cle = titre[:60] + lien[:40]
                    if cle not in vus:
                        vus.add(cle)
                        offres.append({"titre": titre, "entreprise": "Tectra Cameroun", "ville": ville, "date": date, "lien": lien, "source": "Tectra.cm"})
                time.sleep(1)
            except:
                continue
    except Exception as e:
        print(f"Tectra erreur: {e}")
    return offres

# ================================================================
# MICHAEL PAGE AFRICA — CAMEROUN
# ================================================================
def scraper_michaelpage():
    offres = []
    try:
        url = "https://www.michaelpageafrica.com/fr/jobs/cameroon"
        r = requests.get(url, headers=H, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        liens = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/fr/job/" in href or "/fr/jobs/" in href:
                if not href.startswith("http"):
                    href = "https://www.michaelpageafrica.com" + href
                if href not in liens and href != "https://www.michaelpageafrica.com/fr/jobs/cameroon":
                    liens.append(href)
        for lien in liens[:6]:
            try:
                r2 = requests.get(lien, headers=H, timeout=10)
                s2 = BeautifulSoup(r2.text, "html.parser")
                titre_el = s2.find("h1") or s2.find("h2")
                titre = titre_el.get_text(strip=True)[:200] if titre_el else ""
                ville = ""
                entreprise = ""
                date = ""
                for el in s2.find_all(["span", "div", "p", "td", "li"]):
                    txt = el.get_text(strip=True)
                    txt_low = txt.lower()
                    if any(v in txt_low for v in ["yaoundé", "douala", "bafoussam", "cameroun", "cameroon"]):
                        if not ville and len(txt) < 60:
                            ville = txt
                    if any(k in txt_low for k in ["date limite", "expire", "deadline", "posted", "publié"]):
                        if not date and len(txt) < 80:
                            date = txt
                    if any(k in txt_low for k in ["notre client", "client", "société", "entreprise"]):
                        if not entreprise and len(txt) < 100:
                            entreprise = txt
                if titre and len(titre) > 10:
                    cle = titre[:60] + lien[:40]
                    if cle not in vus:
                        vus.add(cle)
                        offres.append({"titre": titre, "entreprise": entreprise, "ville": ville, "date": date, "lien": lien, "source": "Michael Page Africa"})
                time.sleep(1)
            except:
                continue
    except Exception as e:
        print(f"MichaelPage erreur: {e}")
    return offres

# ================================================================
# RELIEFWEB RSS — ONG ET HUMANITAIRE
# ================================================================
def scraper_reliefweb():
    offres = []
    try:
        feed = feedparser.parse("https://reliefweb.int/jobs/rss.xml?country=CM")
        for e in feed.entries[:10]:
            titre = e.get("title", "")[:200]
            lien = e.get("link", "")
            entreprise = ""
            if hasattr(e, "tags"):
                for tag in e.tags:
                    if tag.get("term"):
                        entreprise = tag["term"]
                        break
            if titre and lien and len(titre) > 10:
                cle = titre[:60] + lien[:40]
                if cle not in vus:
                    vus.add(cle)
                    offres.append({"titre": titre, "entreprise": entreprise, "ville": "Cameroun", "date": "", "lien": lien, "source": "ReliefWeb ONG"})
    except Exception as e:
        print(f"ReliefWeb RSS erreur: {e}")
    return offres

# ================================================================
# DEVEX RSS — DEVELOPPEMENT INTERNATIONAL
# ================================================================
def scraper_devex():
    offres = []
    try:
        feed = feedparser.parse("https://www.devex.com/jobs/rss?country_id=43")
        for e in feed.entries[:8]:
            titre = e.get("title", "")[:200]
            lien = e.get("link", "")
            if titre and lien and len(titre) > 10:
                cle = titre[:60] + lien[:40]
                if cle not in vus:
                    vus.add(cle)
                    offres.append({"titre": titre, "entreprise": "", "ville": "Cameroun", "date": "", "lien": lien, "source": "Devex ONG"})
    except Exception as e:
        print(f"Devex erreur: {e}")
    return offres

# ================================================================
# ENVOI TELEGRAM
# ================================================================
async def envoyer():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scraping en cours...")
    toutes = []
    toutes += scraper_reliefweb()
    toutes += scraper_devex()
    toutes += scraper_emploi_cm()
    toutes += scraper_jobincamer()
    toutes += scraper_minajobs()
    toutes += scraper_fne()
    toutes += scraper_jobartis()
    toutes += scraper_tectra()
    toutes += scraper_michaelpage()
    print(f"{len(toutes)} offres trouvees.")
    n = 0
    for o in toutes:
        cle = o["titre"][:60] + o["lien"][:40]
        if cle not in vus:
            vus.add(cle)
            msg = formater(o["titre"], o["entreprise"], o["ville"], o["date"], o["lien"], o["source"])
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
        "❌ Aucune offre serieuse ne demande d'argent avant embauche\n"
        "❌ BoulotCam ne vous contacte JAMAIS en prive\n"
        "❌ Ne payez jamais de frais de dossier\n"
        "❌ Mefiez-vous des numeros inconnus\n\n"
        "✅ Signalez tout comportement suspect dans le groupe\n\n"
        "BoulotCam 🇨🇲 — L'emploi qui travaille pour toi"
    )
    try:
        await bot.send_message(chat_id=CANAL_ID, text=msg)
    except Exception as e:
        print(f"Erreur rappel: {e}")

def job():
    asyncio.run(envoyer())

def job_rappel():
    asyncio.run(rappel())

if __name__ == "__main__":
    print("=" * 50)
    print("BoulotCam Bot demarre...")
    print(f"Canal : {CANAL_ID}")
    print("Sources actives :")
    print("  ✅ Emploi.cm — liens directs")
    print("  ✅ JobInCamer — liens directs")
    print("  ✅ MinaJobs Cameroun — liens directs")
    print("  ✅ FNE Officiel — liens directs")
    print("  ✅ JobArtis Cameroun — liens directs")
    print("  ✅ Tectra Cameroun — liens directs")
    print("  ✅ Michael Page Africa — liens directs")
    print("  ✅ ReliefWeb ONG — RSS")
    print("  ✅ Devex ONG — RSS")
    print("Scan toutes les 10 minutes.")
    print("=" * 50)
    job()
    schedule.every(10).minutes.do(job)
    schedule.every(48).hours.do(job_rappel)
    while True:
        schedule.run_pending()
        time.sleep(30)
