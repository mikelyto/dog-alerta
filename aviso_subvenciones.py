import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from urllib.parse import urljoin
from datetime import datetime, timezone
import os

# =========================
# CONFIGURACIÓN
# =========================
BASE_URL = "https://www.xunta.gal/diario-oficial-galicia/"
KEYWORD = "VI406E"

EMAIL_FROM = os.getenv("EMAIL_USER")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASS = os.getenv("EMAIL_PASS")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465


def get_today_url():
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"{BASE_URL}portalPublicoHome.do?fecha={today}"


def check_dog():
    try:
        url = get_today_url()
        print(f"🔎 Accediendo a: {url}")

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        section_links = []

        for link in soup.find_all("a"):
            href = link.get("href")

            if href and "Secciones" in href:
                full_link = urljoin(BASE_URL, href)
                section_links.append(full_link)

        if not section_links:
            print("⚠️ No se encontraron secciones")
            return None, None

        print(f"📂 Secciones encontradas: {len(section_links)}")

        for section in section_links:
            try:
                print(f"🔎 Analizando: {section}")

                response = requests.get(section, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                for link in soup.find_all("a"):
                    text = link.get_text(strip=True)

                    if KEYWORD in text:
                        full_link = urljoin(BASE_URL, link.get("href"))
                        print("✅ Encontrado")
                        return full_link, text

            except Exception as e:
                print(f"⚠️ Error en sección: {e}")
                continue

        print("ℹ️ No se encontró la keyword")
        return None, None

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None, None


def send_email(link, text):
    try:
        msg = MIMEText(f"{text}\n{link}")
        msg["Subject"] = "DOG - Nueva convocatoria"
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.send_message(msg)

        print("📧 Email enviado")

    except Exception as e:
        print(f"❌ Error email: {e}")


def main():
    link, text = check_dog()

    if link:
        send_email(link, text)
    else:
        print("✔️ Sin novedades")


if __name__ == "__main__":
    main()
