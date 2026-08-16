# -*- coding: utf-8 -*-
"""
Scraper Pharmacies de garde
  - lematin.ma        (Casablanca...)  -> inchangé
  - guidepharmacies.ma (Rabat, Salé, Témara, Ain Aouda) -> parseur réécrit

Changement côté guidepharmacies.ma (2025/2026) :
  chaque ligne de garde contient maintenant DEUX liens :
      <a href="#">Itinéraire →</a>   puis   <a href="https://www.guidepharmacies.ma/rabat-2/pharmacie-xxx.html">Pharmacie XXX - 0537 ...</a>
  L'ancien code prenait le PREMIER <a> => nom = "Itinéraire →", téléphone vide,
  et l'URL de la fiche devenait "https://www.guidepharmacies.ma#" => "Address not found".

Corrections apportées :
  * on identifie le lien de la fiche par son href (et non par sa position)
  * les href sont désormais absolus -> urljoin au lieu de la concaténation
  * détection des sections de date sans dépendre des classes <td class="tableh2">
  * extraction du téléphone depuis le titre ET depuis la fiche
  * extraction des coordonnées GPS depuis le lien Google Maps de la fiche
    -> vrais liens d'itinéraire (Google Maps / Waze / Apple Maps)
  * adresses en arabe correctement gérées (ar = original, fr/en = traduction)
  * cache de traduction + cache des fiches (moins d'appels réseau)
"""

import json
import re
import time
from datetime import date, datetime
from urllib.parse import quote, urljoin, urlparse

import pytz
import requests
from bs4 import BeautifulSoup, NavigableString
from deep_translator import GoogleTranslator

# ---------------------------------------------------------------- CONFIG ----

LEMATIN_BASE_URL = "https://lematin.ma"
GUIDE_BASE_URL = "https://www.guidepharmacies.ma"

LEMATIN_URLS = [
    "https://lematin.ma/pharmacie-garde-casablanca/jour/ain-chock",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/ain-sebaa",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/al-azhar-panorama",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/al-fida",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/annasi",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/belvedere",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/bourgogne",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/hay-hassani",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/hay-mohammadi",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/lissasfa",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/maarif",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/mers-sultan",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/oulfa",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/quartier-des-hopitaux",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/sidi-bernoussi",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/sidi-maarouf",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/sidi-moumen",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/sidi-othmane",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/ain-chock",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/ain-sebaa",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/al-azhar-panorama",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/al-fida",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/annasi",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/belvedere",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/bourgogne",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/hay-hassani",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/hay-mohammadi",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/lissasfa",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/maarif",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/mers-sultan",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/oulfa",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/quartier-des-hopitaux",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/sidi-bernoussi",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/sidi-maarouf",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/sidi-moumen",
    "https://lematin.ma/pharmacie-garde-casablanca/nuit/sidi-othmane",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/afaq",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/ain-itti",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/annakhil",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/azzouzia",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/daoudiate",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/dar-esaada",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/gueliz",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/hay-hassani",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/mhamid",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/medina",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/sidi-youssef-ben-ali",
    "https://lematin.ma/pharmacie-garde/marrakech/jour/targa",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/afaq",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/ain-itti",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/annakhil",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/azzouzia",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/daoudiate",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/dar-esaada",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/gueliz",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/hay-hassani",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/mhamid",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/medina",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/sidi-youssef-ben-ali",
    "https://lematin.ma/pharmacie-garde/marrakech/nuit/targa"
]

# chemin -> nom de ville affiché (évite "Ain-aouda" / "Sale" mal formatés)
GUIDE_CITIES = {
    "/pharmacies-de-garde/rabat.html": "Rabat",
    "/pharmacies-de-garde/sale.html": "Salé",
    "/pharmacies-de-garde/temara.html": "Témara",
    "/pharmacies-de-garde/ain-aouda.html": "Ain Aouda",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,ar;q=0.8,en;q=0.7",
}

# True  = si la page n'affiche pas la garde du jour, on ne publie rien (recommandé)
# False = on publie quand même ce que la page affiche
STRICT_DATE_CHECK = True

REQUEST_TIMEOUT = 25
SLEEP_BETWEEN_REQUESTS = 0.7

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ------------------------------------------------------- DICTIONNAIRES ------

month_mapping = {
    'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12
}

city_translations = {
    'Rabat': {'fr': 'Rabat', 'en': 'Rabat', 'ar': 'الرباط'},
    'Salé': {'fr': 'Salé', 'en': 'Sale', 'ar': 'سلا'},
    'Sale': {'fr': 'Salé', 'en': 'Sale', 'ar': 'سلا'},
    'Témara': {'fr': 'Témara', 'en': 'Temara', 'ar': 'تمارة'},
    'Temara': {'fr': 'Témara', 'en': 'Temara', 'ar': 'تمارة'},
    'Tamesna': {'fr': 'Tamesna', 'en': 'Tamesna', 'ar': 'تامسنا'},
    'Ain Aouda': {'fr': 'Ain Aouda', 'en': 'Ain Aouda', 'ar': 'عين العودة'},
    'Kénitra': {'fr': 'Kénitra', 'en': 'Kenitra', 'ar': 'القنيطرة'},
    'Casablanca': {'fr': 'Casablanca', 'en': 'Casablanca', 'ar': 'الدار البيضاء'},
    'Marrakech': {'fr': 'Marrakech', 'en': 'Marrakech', 'ar': 'مراكش'},
}

pharmacy_translations = {
    'Pharmacie RELAIS DES MEDECINS': {
        'fr': 'Pharmacie RELAIS DES MEDECINS',
        'en': 'Pharmacy RELAIS DES DOCTORS',
        'ar': 'صيدلية راليه دي ميديسين',
    },
}

location_translations = {
    'Aïn Chock': {'fr': 'Aïn Chock', 'en': 'Aïn Chock', 'ar': 'عين الشق'},
    'Aïn Sebaâ': {'fr': 'Aïn Sebaâ', 'en': 'Aïn Sebaâ', 'ar': 'عين السبع'},
    'Al Azhar Panorama': {'fr': 'Al Azhar Panorama', 'en': 'Al Azhar Panorama', 'ar': 'الأزهر بانوراما'},
    'Al Fida': {'fr': 'Al Fida', 'en': 'Al Fida', 'ar': 'الفداء'},
    'Annasi': {'fr': 'Annasi', 'en': 'Annasi', 'ar': 'أناسي'},
    'Belvédère': {'fr': 'Belvédère', 'en': 'Belvédère', 'ar': 'بيلفيدير'},
    'Bourgogne': {'fr': 'Bourgogne', 'en': 'Bourgogne', 'ar': 'بورغون'},
    'Hay Hassani': {'fr': 'Hay Hassani', 'en': 'Hay Hassani', 'ar': 'حي الحسني'},
    'Hay Mohammadi': {'fr': 'Hay Mohammadi', 'en': 'Hay Mohammadi', 'ar': 'حي المحمدي'},
    'Lissasfa': {'fr': 'Lissasfa', 'en': 'Lissasfa', 'ar': 'ليساسفا'},
    'Maarif': {'fr': 'Maarif', 'en': 'Maarif', 'ar': 'المعاريف'},
    'Mers Sultan': {'fr': 'Mers Sultan', 'en': 'Mers Sultan', 'ar': 'مرس السلطان'},
    'Oulfa': {'fr': 'Oulfa', 'en': 'Oulfa', 'ar': 'ولفا'},
    'Quartier des Hôpitaux': {'fr': 'Quartier des Hôpitaux', 'en': 'Quartier des Hôpitaux', 'ar': 'حي المستشفيات'},
    'Sidi Bernoussi': {'fr': 'Sidi Bernoussi', 'en': 'Sidi Bernoussi', 'ar': 'سيدي برنوصي'},
    'Sidi Maarouf': {'fr': 'Sidi Maarouf', 'en': 'Sidi Maarouf', 'ar': 'سيدي معروف'},
    'Sidi Moumen': {'fr': 'Sidi Moumen', 'en': 'Sidi Moumen', 'ar': 'سيدي مومن'},
    'Sidi Othmane': {'fr': 'Sidi Othmane', 'en': 'Sidi Othmane', 'ar': 'سيدي عثمان'},
    'Ain itti': {'fr': 'Ain itti', 'en': 'Ain itti', 'ar': 'عين إيتي'},
    'Daoudiate': {'fr': 'Daoudiate', 'en': 'Daoudiate', 'ar': 'الداوية'},
    'Guéliz': {'fr': 'Guéliz', 'en': 'Guéliz', 'ar': 'ڭليز'},
    'HAY AL FADL': {'fr': 'HAY AL FADL', 'en': 'HAY AL FADL', 'ar': 'حي الفضل'},
    "M'Hamid": {'fr': "M'Hamid", 'en': "M'Hamid", 'ar': 'مْحاميد'},
    'Medina': {'fr': 'Medina', 'en': 'Medina', 'ar': 'المدينة'},
    'Sidi Ghanem': {'fr': 'Sidi Ghanem', 'en': 'Sidi Ghanem', 'ar': 'سيدي غانم'},
    'Sidi Youssef Ben Ali': {'fr': 'Sidi Youssef Ben Ali', 'en': 'Sidi Youssef Ben Ali', 'ar': 'سيدي يوسف بن علي'},
    'Targa': {'fr': 'Targa', 'en': 'Targa', 'ar': 'تارڭا'},
    # quartiers Rabat / Salé / Témara fréquents
    'Agdal': {'fr': 'Agdal', 'en': 'Agdal', 'ar': 'أكدال'},
    'Hay Riad': {'fr': 'Hay Riad', 'en': 'Hay Riad', 'ar': 'حي الرياض'},
    'Centre Ville': {'fr': 'Centre Ville', 'en': 'City Center', 'ar': 'وسط المدينة'},
    'Akkari-Ocean': {'fr': 'Akkari-Ocean', 'en': 'Akkari-Ocean', 'ar': 'العكاري - المحيط'},
    'Ocean-Orangers': {'fr': 'Ocean-Orangers', 'en': 'Ocean-Orangers', 'ar': 'المحيط - أورونجي'},
    'Yacoub El Mansour': {'fr': 'Yacoub El Mansour', 'en': 'Yacoub El Mansour', 'ar': 'يعقوب المنصور'},
    'Takadoum & Souissi': {'fr': 'Takadoum & Souissi', 'en': 'Takadoum & Souissi', 'ar': 'التقدم والسويسي'},
    'Akkari-Ocean-Orangers': {'fr': 'Akkari-Ocean-Orangers', 'en': 'Akkari-Ocean-Orangers', 'ar': 'العكاري - المحيط - أورونجي'},
    'Souissi': {'fr': 'Souissi', 'en': 'Souissi', 'ar': 'السويسي'},
    'Takadoum': {'fr': 'Takadoum', 'en': 'Takadoum', 'ar': 'التقدم'},
    # Salé
    'Al Mohit Abouab Sala': {'fr': 'Al Mohit Abouab Sala', 'en': 'Al Mohit Abouab Sala', 'ar': 'المحيط أبواب سلا'},
    'Bettana': {'fr': 'Bettana', 'en': 'Bettana', 'ar': 'بطانة'},
    'El Mazza Sidi Abdellah': {'fr': 'El Mazza Sidi Abdellah', 'en': 'El Mazza Sidi Abdellah', 'ar': 'المزة سيدي عبد الله'},
    'Hay Arrahma': {'fr': 'Hay Arrahma', 'en': 'Hay Arrahma', 'ar': 'حي الرحمة'},
    'Hay Chmaou': {'fr': 'Hay Chmaou', 'en': 'Hay Chmaou', 'ar': 'حي شماعو'},
    'Hay Essalam': {'fr': 'Hay Essalam', 'en': 'Hay Essalam', 'ar': 'حي السلام'},
    'Hay Elinbiate': {'fr': 'Hay Elinbiate', 'en': 'Hay Elinbiate', 'ar': 'حي الإنبعاث'},
    'My Ismail': {'fr': 'My Ismail', 'en': 'My Ismail', 'ar': 'مولاي إسماعيل'},
    'Salé Médina': {'fr': 'Salé Médina', 'en': 'Sale Medina', 'ar': 'مدينة سلا'},
    'Tabriquet': {'fr': 'Tabriquet', 'en': 'Tabriquet', 'ar': 'تبريكت'},
    # Témara / Tamesna / Ain Aouda
    'Centre': {'fr': 'Centre', 'en': 'Center', 'ar': 'المركز'},
    'Centre Al Wifak': {'fr': 'Centre Al Wifak', 'en': 'Centre Al Wifak', 'ar': 'مركز الوفاق'},
    'El Guich Oudaya': {'fr': 'El Guich Oudaya', 'en': 'El Guich Oudaya', 'ar': 'الكيش أوداية'},
    'El Massira': {'fr': 'El Massira', 'en': 'El Massira', 'ar': 'المسيرة'},
    'Harhoura': {'fr': 'Harhoura', 'en': 'Harhoura', 'ar': 'الهرهورة'},
    'Oulad Mtaâ': {'fr': 'Oulad Mtaâ', 'en': 'Oulad Mtaa', 'ar': 'أولاد مطاع'},
    'Tamesna': {'fr': 'Tamesna', 'en': 'Tamesna', 'ar': 'تامسنا'},
}

# quartiers rencontrés sans traduction connue (affichés en fin d'exécution)
UNKNOWN_LOCATIONS = set()

hours_translations = {
    "Day et Nuit": {"fr": "24h/24h", "en": "24h/24h", "ar": "24h/24h"},
    "Day": {"fr": "09h00 - 00h00", "en": "09h00 - 00h00", "ar": "09h00 - 00h00"},
    "Nuit": {"fr": "24h/24h", "en": "24h/24h", "ar": "24h/24h"},
    "Unknown": {"fr": "aucune", "en": "none", "ar": "غير متوفر"},
}

NO_ADDRESS = {"Address not found", "Address unavailable", ""}

# ------------------------------------------------------------ HELPERS -------

ARABIC_RE = re.compile(r'[\u0600-\u06FF]')
PHONE_RE = re.compile(r'(?:\+212|00212|0)\s?\d(?:[\s.\-]?\d){7,8}')
WEEKDAYS = r'(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)'
MONTHS = r'(?:janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre)'
DATE_RE = re.compile(
    rf'(?:{WEEKDAYS}\s+)?(\d{{1,2}})\s+({MONTHS})\s+(\d{{4}})', re.IGNORECASE
)
HOUR_PATTERNS = [
    re.compile(r'24\s*h\s*/\s*24\s*h?', re.IGNORECASE),
    re.compile(r'(\d{1,2})\s*h\s*(\d{2})?\s*(?:à|a|-|–|:)\s*(\d{1,2})\s*h\s*(\d{2})?', re.IGNORECASE),
]

_translation_cache = {}
_detail_cache = {}


def clean(text):
    """Espaces normalisés."""
    return ' '.join((text or '').split())


def has_arabic(text):
    return bool(ARABIC_RE.search(text or ''))


def get_soup(url, retries=3):
    """GET + BeautifulSoup avec retries."""
    last_error = None
    for attempt in range(retries):
        try:
            response = SESSION.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    print(f"  ! Échec du chargement de {url} : {last_error}")
    return None


def auto_translate(text, target_lang, source='auto'):
    """Google Translate avec cache. 'auto' gère aussi les textes en arabe."""
    if not text or text in NO_ADDRESS:
        return text
    key = (text, target_lang)
    if key in _translation_cache:
        return _translation_cache[key]
    try:
        translated = GoogleTranslator(source=source, target=target_lang).translate(text)
        translated = translated or text
    except Exception as exc:  # noqa: BLE001
        print(f"  ! Traduction impossible pour '{text[:40]}...' : {exc}")
        translated = text
    _translation_cache[key] = translated
    return translated


def normalize_pharmacy_name(name):
    name = clean(name)
    if name.lower().startswith('pharmacie '):
        name = name[10:]
    return name.strip()


def get_pharmacy_translation(name, translations=None):
    translations = translations if translations is not None else pharmacy_translations
    normalized_name = normalize_pharmacy_name(name)
    if not normalized_name:
        # le lien ne contenait que le mot "Pharmacie"
        return {'fr': 'Pharmacie', 'en': 'Pharmacy', 'ar': 'صيدلية'}

    for key in (f"Pharmacie {normalized_name}", f"PHARMACIE {normalized_name}", normalized_name):
        if key in translations:
            return translations[key]

    lowered = normalized_name.lower()
    for key in translations:
        if normalize_pharmacy_name(key).lower() == lowered:
            return translations[key]

    capitalized = normalized_name.title()

    # ex. "LA GRANDE PHARMACIE DE TEMARA" : le mot pharmacie est déjà dans le nom
    if 'pharmaci' in normalized_name.lower():
        return {
            'fr': capitalized,
            'en': capitalized,
            'ar': auto_translate(capitalized, 'ar'),
        }

    fr_name = f"Pharmacie {capitalized}"
    return {
        'fr': fr_name,
        'en': f"{capitalized} Pharmacy",
        'ar': f"صيدلية {auto_translate(capitalized, 'ar')}",
    }


def translate_field(field, value):
    translation_map = {
        'city': city_translations,
        'pharmacy': pharmacy_translations,
        'location': location_translations,
        'hours': hours_translations,
    }

    if field == 'hours':
        translations = translation_map['hours']
        if value in translations:
            return translations[value]
        return {"fr": value, "en": value, "ar": value}

    if field == 'pharmacy':
        return get_pharmacy_translation(value, translation_map['pharmacy'])

    translations = translation_map.get(field, {})
    if value in translations:
        return translations[value]
    if not value:
        return {"fr": "", "en": "", "ar": ""}

    if field == 'location':
        # un quartier est un nom propre : Google Translate le massacre
        # ("Hay Arrahma" -> "There is Arrahma"). On garde l'original.
        UNKNOWN_LOCATIONS.add(value)
        return {"fr": value, "en": value, "ar": value}

    return {
        "fr": value,
        "en": auto_translate(value, 'en'),
        "ar": auto_translate(value, 'ar'),
    }


def translate_address(address):
    """Les fiches de guidepharmacies.ma sont parfois en arabe, parfois en français."""
    if not address or address in NO_ADDRESS:
        return {"fr": address, "en": address, "ar": address}
    if has_arabic(address):
        return {
            "fr": auto_translate(address, 'fr'),
            "en": auto_translate(address, 'en'),
            "ar": address,
        }
    return {
        "fr": address,
        "en": auto_translate(address, 'en'),
        "ar": auto_translate(address, 'ar'),
    }


def generate_maps_links(name, city, lat=None, lng=None):
    """Liens d'itinéraire : coordonnées GPS si disponibles, sinon recherche texte."""
    if lat is not None and lng is not None:
        dest = f"{lat},{lng}"
        return {
            "google_maps": f"https://www.google.com/maps/dir/?api=1&destination={dest}",
            "waze": f"https://waze.com/ul?ll={dest}&navigate=yes",
            "apple_maps": f"http://maps.apple.com/?daddr={dest}&dirflg=d",
        }
    encoded_query = quote(clean(f"{name} {city}"))
    return {
        "google_maps": f"https://www.google.com/maps/search/?api=1&query={encoded_query}",
        "waze": f"https://www.waze.com/ul?q={encoded_query}&navigate=yes",
        "apple_maps": f"http://maps.apple.com/?q={encoded_query}",
    }


MAPS_MESSAGE = {
    "fr": "Cliquez pour obtenir l'itinéraire sur:",
    "en": "Click to get directions on:",
    "ar": "انقر للحصول على الاتجاهات على:",
}

# ------------------------------------------------------------ LEMATIN -------

def get_lematin_pharmacy_links():
    pharmacy_links = []
    for url in LEMATIN_URLS:
        try:
            shift = 'jour' if '/jour/' in url else 'nuit' if '/nuit/' in url else 'unknown'
            soup = get_soup(url)
            if soup is None:
                continue
            for record in soup.select('div.pharmacies div.ph-record'):
                link_tag = record.select_one('div.ph-name a')
                if not link_tag or not link_tag.get('href'):
                    continue
                pharmacy_links.append({
                    'url': urljoin(LEMATIN_BASE_URL, link_tag['href']),
                    'shift': shift,
                })
            time.sleep(SLEEP_BETWEEN_REQUESTS)
        except Exception as exc:  # noqa: BLE001
            print(f"Error fetching {url}: {exc}")
    return pharmacy_links


def parse_lematin_pharmacy(url, shift):
    try:
        soup = get_soup(url)
        if soup is None:
            return None

        hours_key = 'Day' if shift == 'jour' else 'Nuit' if shift == 'nuit' else 'Unknown'

        data = {
            "city": {"fr": "", "en": "", "ar": ""},
            "name": {"fr": "", "en": "", "ar": ""},
            "location": {"fr": "", "en": "", "ar": ""},
            "phone": "",
            "phones": [],
            "hours": translate_field('hours', hours_key),
            "address": {"fr": "", "en": "", "ar": ""},
            "coordinates": None,
            "maps": {"message": MAPS_MESSAGE, "links": {}},
        }

        name_tag = soup.select_one('.record.pharmacy-name')
        if name_tag:
            raw_parts = [
                clean(t) for t in name_tag.find_all(string=True, recursive=True)
                if "Modifier ou compléter" not in t
            ]
            raw_name = clean(" ".join(p for p in raw_parts if p))
            data["name"] = translate_field('pharmacy', raw_name)

        for detail in soup.select('.ph-details p'):
            text = detail.get_text(strip=True)
            if 'Tel:' in text or 'Tél:' in text:
                phone = clean(text.split(':', 1)[-1])
                data["phone"] = phone
                data["phones"] = [phone] if phone else []
            elif 'Adresse:' in text:
                data["address"] = translate_address(clean(text.split(':', 1)[-1]))
            elif 'Quartier:' in text:
                data["location"] = translate_field('location', clean(text.split(':', 1)[-1]))
            elif 'Ville:' in text:
                data["city"] = translate_field('city', clean(text.split(':', 1)[-1]))

        if data["name"]["fr"] and data["city"]["fr"]:
            data["maps"]["links"] = generate_maps_links(data["name"]["fr"], data["city"]["fr"])

        return data
    except Exception as exc:  # noqa: BLE001
        print(f"Error parsing {url}: {exc}")
        return None


def scrape_lematin():
    result = []
    print("Collecting pharmacy links from LeMatin...")
    links = get_lematin_pharmacy_links()
    print(f"Found {len(links)} pharmacies on LeMatin. Starting scraping...")
    for i, link_info in enumerate(links, 1):
        print(f"  LeMatin {i}/{len(links)}")
        pharmacy_data = parse_lematin_pharmacy(link_info['url'], link_info['shift'])
        if pharmacy_data:
            result.append(pharmacy_data)
        time.sleep(SLEEP_BETWEEN_REQUESTS)
    return result

# ------------------------------------------------- GUIDEPHARMACIES.MA -------

def parse_french_date(text):
    """'Dimanche 16 Août 2026' -> date(2026, 8, 16). None si pas une date."""
    match = DATE_RE.search(text or '')
    if not match:
        return None
    day, month_name, year = match.groups()
    month = month_mapping.get(month_name.lower().replace('û', 'u').replace('é', 'e')) \
        or month_mapping.get(month_name.lower())
    if not month:
        return None
    try:
        return datetime(int(year), month, int(day)).date()
    except ValueError:
        return None


def is_pharmacy_link(href):
    """True uniquement pour les fiches pharmacie (pas '#', pas le menu, pas Google Maps)."""
    if not href:
        return False
    href = href.strip()
    if href.startswith('#') or href.lower().startswith(('javascript:', 'mailto:', 'tel:')):
        return False
    parsed = urlparse(href)
    if parsed.netloc and 'guidepharmacies.ma' not in parsed.netloc:
        return False
    path = parsed.path.lower()
    if not path.endswith('.html'):
        return False
    if '/pharmacies-de-garde/' in path:   # pages de listing / menu
        return False
    slug = path.rsplit('/', 1)[-1]
    return 'pharmacie' in slug or 'phie' in slug


def normalize_hours(text):
    """'24h/24h', '9h à 00h00', '9h à 23h00'... -> chaîne propre, '' si absent."""
    text = clean(text)
    if not text:
        return ''
    if HOUR_PATTERNS[0].search(text):
        return '24h/24h'
    match = HOUR_PATTERNS[1].search(text)
    if match:
        sh, sm, eh, em = match.groups()
        sm = sm or '00'
        em = em or '00'
        return f"{int(sh)}h à {int(eh):02d}h{em}"
    return ''


def split_location_hours(text):
    """'Akkari-Ocean (9h à 00h00)' -> ('Akkari-Ocean', '9h à 00h00')"""
    text = clean(text)
    if not text:
        return '', ''
    hours = normalize_hours(text)
    if hours:
        for pattern in HOUR_PATTERNS:
            text = pattern.sub(' ', text)
    text = re.sub(r'\(\s*\)', ' ', text)
    text = re.sub(r'[()]', ' ', text)
    text = re.sub(r'\(\d+\)', ' ', text)
    location = clean(text).strip(' -–—:•|')
    return location, hours


def split_name_phone(text):
    """'Pharmacie IBN YASSINE - 0537 77 27 43' -> ('Pharmacie IBN YASSINE', '0537 77 27 43')"""
    text = clean(text)
    phones = PHONE_RE.findall(text)
    name = text
    if phones:
        name = clean(PHONE_RE.sub(' ', text)).strip(' -–—:,')
    name = re.sub(r'\s*[-–—]\s*$', '', name).strip()
    phones = [clean(p) for p in phones]
    return name, phones


def extract_latlng(href):
    """Récupère lat/lng depuis une URL Google Maps."""
    if not href:
        return None
    patterns = [
        r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)',
        r'@(-?\d+\.\d+),(-?\d+\.\d+)',
        r'[?&](?:q|ll|daddr|destination|center)=(-?\d+\.\d+),\s*(-?\d+\.\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, href)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            # garde-fou : Maroc
            if 20 <= lat <= 37 and -18 <= lng <= 0:
                return lat, lng
    return None


def fetch_guide_detail(url):
    """Fiche pharmacie : adresse, téléphones, coordonnées GPS."""
    if url in _detail_cache:
        return _detail_cache[url]

    detail = {'address': 'Address not found', 'phones': [], 'lat': None, 'lng': None, 'title': ''}
    soup = get_soup(url)
    if soup is None:
        detail['address'] = 'Address unavailable'
        _detail_cache[url] = detail
        return detail

    heading = soup.select_one('h1.eb-page-heading') or soup.select_one('.eb-box-heading h1') or soup.find('h1')
    if heading:
        detail['title'] = clean(heading.get_text(' ', strip=True))

    container = (soup.select_one('.eb-description-details')
                 or soup.select_one('#eb-event-details')
                 or soup.select_one('.eb-description'))

    search_zone = container or soup
    for anchor in search_zone.find_all('a', href=True):
        coords = extract_latlng(anchor['href'])
        if coords:
            detail['lat'], detail['lng'] = coords
            break

    if container:
        address_lines = []
        phones = []
        for raw_line in container.get_text('\n', strip=True).split('\n'):
            line = clean(raw_line)
            if not line:
                continue
            found = PHONE_RE.findall(line)
            phones.extend(clean(p) for p in found)
            stripped = clean(PHONE_RE.sub(' ', line))
            stripped = re.sub(r'^\s*(t[ée]l|tel|phone|gsm|fix)\s*[:.]?\s*', '', stripped, flags=re.IGNORECASE)
            stripped = stripped.strip(' -–—:.,|')
            # on ignore les lignes qui ne contenaient qu'un numéro / un libellé "Tél"
            if len(stripped) <= 3:
                continue
            if detail['title'] and detail['title'] in stripped:
                continue
            address_lines.append(stripped)

        # dédoublonnage en gardant l'ordre
        address_lines = list(dict.fromkeys(address_lines))
        detail['phones'] = list(dict.fromkeys(phones))
        if address_lines:
            detail['address'] = ' | '.join(address_lines)

    _detail_cache[url] = detail
    return detail


def entry_container(anchor):
    """Remonte jusqu'au bloc qui contient le quartier + les horaires de CETTE pharmacie."""
    anchor_text_len = len(clean(anchor.get_text(' ', strip=True)))
    node = anchor.parent
    best = anchor.parent
    while node is not None and node.name not in ('body', 'html', '[document]'):
        pharmacy_anchors = [a for a in node.find_all('a', href=True) if is_pharmacy_link(a.get('href'))]
        if len(pharmacy_anchors) > 1:
            break
        best = node
        text = clean(node.get_text(' ', strip=True))
        if len(text) > anchor_text_len + 2:
            return node
        node = node.parent
    return best


def extract_guide_entries(soup):
    """Parcourt le document dans l'ordre : sections de date + liens de fiches.

    Renvoie (entries, header_dates) où header_dates = les dates de section
    réellement présentes sur la page (l'intitulé de semaine
    "Lundi 10 Août 2026 - Dimanche 16 Août 2026" contient 2 dates : ignoré).
    """
    entries = []
    header_dates = []
    current_date = None

    for node in soup.descendants:
        if isinstance(node, NavigableString):
            text = clean(str(node))
            if not text or len(text) > 80:
                continue
            matches = DATE_RE.findall(text)
            if len(matches) == 1:                      # une seule date = en-tête de jour
                parsed = parse_french_date(text)       # (2 dates = plage de semaine)
                if parsed:
                    current_date = parsed
                    if parsed not in header_dates:
                        header_dates.append(parsed)
        elif getattr(node, 'name', None) == 'a' and is_pharmacy_link(node.get('href')):
            entries.append({'date': current_date, 'anchor': node})

    return entries, header_dates


def build_guide_pharmacy(anchor, city_name, base_url):
    container = entry_container(anchor)

    # texte du bloc, sans le texte des liens ("Itinéraire →" et le nom)
    block_text = clean(container.get_text(' ', strip=True))
    for link in container.find_all('a'):
        link_text = clean(link.get_text(' ', strip=True))
        if link_text:
            block_text = block_text.replace(link_text, ' ')
    block_text = re.sub(r'itin[ée]raire|→|➔|>>|»', ' ', block_text, flags=re.IGNORECASE)

    location, hours = split_location_hours(block_text)

    # repli : quartier / horaires placés dans un élément voisin (colonne séparée, badge...)
    if not location or not hours:
        sibling = container.previous_sibling
        checked = 0
        while sibling is not None and checked < 3:
            if getattr(sibling, 'get_text', None):
                sibling_text = clean(sibling.get_text(' ', strip=True))
                if sibling_text and not sibling.find('a', href=True):
                    alt_location, alt_hours = split_location_hours(sibling_text)
                    location = location or alt_location
                    hours = hours or alt_hours
                checked += 1
            sibling = sibling.previous_sibling

    name, phones_from_title = split_name_phone(anchor.get_text(' ', strip=True))

    detail_url = urljoin(base_url, anchor['href'])
    detail = fetch_guide_detail(detail_url)
    time.sleep(SLEEP_BETWEEN_REQUESTS)

    if not name and detail['title']:
        name, phones_from_title = split_name_phone(detail['title'])

    phones = list(dict.fromkeys(phones_from_title + detail['phones']))

    name_trans = translate_field('pharmacy', name)
    city_trans = translate_field('city', city_name)
    location_trans = translate_field('location', location) if location else {"fr": "", "en": "", "ar": ""}
    address_trans = translate_address(detail['address'])

    coordinates = None
    if detail['lat'] is not None and detail['lng'] is not None:
        coordinates = {"lat": detail['lat'], "lng": detail['lng']}

    return {
        'city': city_trans,
        'name': name_trans,
        'location': location_trans,
        'phone': phones[0] if phones else '',
        'phones': phones,
        'hours': hours or '',
        'address': address_trans,
        'coordinates': coordinates,
        'maps': {
            'message': MAPS_MESSAGE,
            'links': generate_maps_links(
                name_trans['fr'], city_trans['fr'], detail['lat'], detail['lng']
            ),
        },
    }


def scrape_guide_city(city_path, city_name, target_date):
    """La page publique affiche UNIQUEMENT la garde du jour.

    ATTENTION : ne pas ajouter de paramètre ?date=... — le site l'interprète
    comme le début de la semaine et renvoie la garde du LUNDI (c'est ce qui
    faisait remonter de mauvaises pharmacies).
    """
    url = f"{GUIDE_BASE_URL}{city_path}"
    soup = get_soup(url)
    if soup is None:
        return []

    entries, header_dates = extract_guide_entries(soup)
    if not entries:
        print(f"  ! Aucune pharmacie trouvée sur la page {city_name}")
        return []

    if len(header_dates) > 1:
        # plusieurs journées présentes : on ne garde que celle du jour
        selected = [e for e in entries if e['date'] == target_date]
        if not selected:
            print(f"  ! Aucune section pour le {target_date.isoformat()} ({city_name}) "
                  f"— sections trouvées : {[d.isoformat() for d in header_dates]}")
            return []
    elif header_dates and header_dates[0] != target_date:
        # la page affiche un autre jour : mieux vaut ne rien publier que du faux
        print(f"  ! {city_name} affiche le {header_dates[0].isoformat()} et non le "
              f"{target_date.isoformat()} — données ignorées")
        if STRICT_DATE_CHECK:
            return []
        selected = entries
    else:
        if not header_dates:
            print(f"  ! Aucune date détectée sur la page {city_name} — on garde la liste affichée.")
        selected = entries

    pharmacies = []
    seen = set()
    for entry in selected:
        href = urljoin(url, entry['anchor']['href'])
        if href in seen:
            continue
        seen.add(href)
        try:
            pharmacies.append(build_guide_pharmacy(entry['anchor'], city_name, url))
        except Exception as exc:  # noqa: BLE001
            print(f"  ! Erreur sur {href} : {exc}")
    return pharmacies


def scrape_guide():
    result = []
    target_date = datetime.now(pytz.timezone('Africa/Casablanca')).date()
    print(f"\nFetching pharmacies from GuidePharmacies for: {target_date.strftime('%d/%m/%Y')}")

    for city_path, city_name in GUIDE_CITIES.items():
        print(f"Checking {city_name}...")
        pharmacies = scrape_guide_city(city_path, city_name, target_date)
        print(f"  -> {len(pharmacies)} pharmacie(s)")
        result.extend(pharmacies)

    return result

# --------------------------------------------------------------- MAIN -------

def main():
    all_pharmacies = {
        "date": datetime.now(pytz.timezone('Africa/Casablanca')).date().isoformat(),
        "sources": {
            "lematin": {"pharmacies": scrape_lematin()},
            "guide": {"pharmacies": scrape_guide()},
        },
    }

    all_pharmacies["total_pharmacies"] = (
        len(all_pharmacies["sources"]["lematin"]["pharmacies"])
        + len(all_pharmacies["sources"]["guide"]["pharmacies"])
    )

    filename = f'pharmacies_{date.today().isoformat()}.json'
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(all_pharmacies, file, ensure_ascii=False, indent=2)

    print(f"\nData has been saved to {filename}")
    print(f"Total pharmacies found: {all_pharmacies['total_pharmacies']}")
    print(f"- LeMatin: {len(all_pharmacies['sources']['lematin']['pharmacies'])}")
    print(f"- GuidePharmacies: {len(all_pharmacies['sources']['guide']['pharmacies'])}")

    if UNKNOWN_LOCATIONS:
        print("\nQuartiers sans traduction (à ajouter dans location_translations) :")
        for location in sorted(UNKNOWN_LOCATIONS):
            print(f"    '{location}': {{'fr': '{location}', 'en': '{location}', 'ar': ''}},")


if __name__ == "__main__":
    main()
