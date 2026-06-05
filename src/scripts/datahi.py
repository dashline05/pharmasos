import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from urllib.parse import urljoin, quote
import re
import json
import time
import pytz
from deep_translator import GoogleTranslator

# Global Headers to prevent blocking
GLOBAL_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive'
}

# Base URLs
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

GUIDE_CITIES_BASE = ["rabat", "sale", "temara", "ain-aouda"]

month_mapping = {
    'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12
}

city_translations = {
    'Rabat': {'fr': 'Rabat', 'en': 'Rabat', 'ar': 'الرباط'},
    'Sale': {'fr': 'Sale', 'en': 'Sale', 'ar': 'سلا'},
    'Temara': {'fr': 'Temara', 'en': 'Temara', 'ar': 'تمارة'},
    'Casablanca': {'fr': 'Casablanca', 'en': 'Casablanca', 'ar': 'الدار البيضاء'},
    'Marrakech': {'fr': 'Marrakech', 'en': 'Marrakech', 'ar': 'مراكش'},
    'Ain-aouda': {'fr': 'Ain-aouda', 'en': 'Ain-aouda', 'ar': 'عين عودة'}
}

hours_translations = {
    "Day et Nuit": {"fr": "24h/24h", "en": "24h/24h", "ar": "24h/24h"},
    "Day": {"fr": "09h00 - 00h00", "en": "09h00 - 00h00", "ar": "09h00 - 00h00"},
    "Nuit": {"fr": "24h/24h", "en": "24h/24h", "ar": "24h/24h"},
    "Unknown": {"fr": "aucune", "en": "none", "ar": "غير متوفر"}
}

def auto_translate(text, target_lang):
    if not text or text in ["Address not found", "Address unavailable"]:
        return text
    try:
        return GoogleTranslator(source='fr', target=target_lang).translate(text)
    except Exception:
        return text

def normalize_pharmacy_name(name):
    name = ' '.join(name.split())
    if name.lower().startswith('pharmacie '):
        name = name[10:]
    return name.strip()

def get_pharmacy_translation(name):
    normalized_name = normalize_pharmacy_name(name)
    capitalized_name = normalized_name.title()
    fr_name = f"Pharmacie {capitalized_name}"
    en_name = f"{capitalized_name} Pharmacy"
    ar_name = auto_translate(fr_name, 'ar')
    return {'fr': fr_name, 'en': en_name, 'ar': ar_name}

def translate_field(field, value):
    if field == 'hours':
        if value in hours_translations:
            return hours_translations[value]
        return {"fr": value, "en": value, "ar": value}

    if field == 'pharmacy':
        return get_pharmacy_translation(value)
    
    if field == 'city':
        if value in city_translations:
            return city_translations[value]
            
    en_val = auto_translate(value, 'en')
    ar_val = auto_translate(value, 'ar')
    return {"fr": value, "en": en_val, "ar": ar_val}

def generate_maps_links(name, city):
    query = f"{name} {city}"
    encoded_query = quote(query)
    return {
        "google_maps": f"https://www.google.com/maps/search/?api=1&query={encoded_query}",
        "waze": f"https://www.waze.com/ul?q={encoded_query}&navigate=yes",
        "apple_maps": f"http://maps.apple.com/?q={encoded_query}"
    }

# LeMatin scraping functions
def get_lematin_pharmacy_links():
    pharmacy_links = []
    for url in LEMATIN_URLS:
        try:
            shift = 'jour' if '/jour/' in url else 'nuit' if '/nuit/' in url else 'unknown'
            response = requests.get(url, headers=GLOBAL_HEADERS, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            records = soup.select('div.pharmacies div.ph-record')
            
            for record in records:
                link_tag = record.select_one('div.ph-name a')
                if link_tag and 'href' in link_tag.attrs:
                    full_url = urljoin(LEMATIN_BASE_URL, link_tag['href'])
                    pharmacy_links.append({'url': full_url, 'shift': shift})
            time.sleep(0.5)
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
    return pharmacy_links

def parse_lematin_pharmacy(url, shift):
    try:
        response = requests.get(url, headers=GLOBAL_HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        hours_key = 'Day' if shift == 'jour' else 'Nuit' if shift == 'nuit' else 'Unknown'
        
        data = {
            "city": {"fr": "", "en": "", "ar": ""},
            "name": {"fr": "", "en": "", "ar": ""},
            "location": {"fr": "", "en": "", "ar": ""},
            "phone": None,
            "hours": translate_field('hours', hours_key),
            "address": {"fr": "", "en": "", "ar": ""},
            "maps": {"message": {"fr": "Cliquez pour obtenir l'itinéraire sur:", "en": "Click to get directions on:", "ar": "انقر للحصول على الاتجاهات على:"}, "links": {}}
        }

        name_tag = soup.select_one('.record.pharmacy-name')
        if name_tag:
            raw_parts = [text.strip() for text in name_tag.find_all(text=True, recursive=True) if "Modifier ou compléter" not in text]
            raw_name = " ".join(raw_parts).strip()
            data["name"] = translate_field('pharmacy', raw_name)

        details = soup.select('.ph-details p')
        for detail in details:
            text = detail.get_text(strip=True)
            if 'Tel:' in text:
                data["phone"] = text.split(':')[-1].strip()
            elif 'Adresse:' in text:
                address = text.split(':')[-1].strip()
                data["address"] = translate_field('address', address)
            elif 'Quartier:' in text:
                location = text.split(':')[-1].strip()
                data["location"] = translate_field('location', location)
            elif 'Ville:' in text:
                city = text.split(':')[-1].strip()
                data["city"] = translate_field('city', city)

        if data["name"]["fr"] and data["city"]["fr"]:
            data["maps"]["links"] = generate_maps_links(data["name"]["fr"], data["city"]["fr"])
        return data
    except Exception as e:
        print(f"Error parsing {url}: {str(e)}")
        return None

# Guide Pharmacies scraping functions
def parse_french_date(date_str):
    parts = re.split(r'\s+', date_str.strip())
    day = int(parts[1])
    month = month_mapping[parts[2].lower()]
    year = int(parts[3])
    return datetime(year, month, day).date()

def parse_location_hours(text):
    text = text.strip()
    if not text:
        return '', ''
    text = re.sub(r'\(\d+\)', '', text).strip()
    
    hour_patterns = [r'24h/24h', r'\d+h à \d+h', r'\d+h à \d+h:\d+']
    hours = ''
    for pattern in hour_patterns:
        match = re.search(pattern, text)
        if match:
            hours = match.group(0).strip()
            text = text.replace(hours, '').strip()
            break
    
    if not hours and '(' in text:
        parts = text.split('(', 1)
        location = parts[0].strip() if len(parts) > 1 else text.strip()
        hours = parts[1].replace(')', '').strip() if len(parts) > 1 else ''
    else:
        location = text.strip()
    return location, hours

def parse_name_phone(text):
    parts = text.split(' - ', 1)
    return parts[0].strip(), parts[1].strip() if len(parts) > 1 else ''

def fetch_pharmacy_address(url):
    try:
        response = requests.get(url, headers=GLOBAL_HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        description_div = soup.find('div', {'class': 'eb-description-details'})
        if description_div:
            address_paragraphs = description_div.find_all('p', style=re.compile(r'text-align:\s*center', re.IGNORECASE))
            address_lines = [p.get_text(strip=True) for p in address_paragraphs if 'Tél:' not in p.get_text()]
            return ' | '.join(address_lines) or "Address not found"
        return "Address not found"
    except Exception:
        return "Address unavailable"

def extract_guide_pharmacy_data(soup, city_name, target_date):
    pharmacies = []
    date_sections = soup.find_all('td', {'class': 'tableh2'})
    
    # Accept today OR yesterday to handle late night shifts
    allowed_dates = [target_date, target_date - timedelta(days=1)]

    for date_section in date_sections:
        date_text = date_section.get_text(strip=True)
        try:
            section_date = parse_french_date(date_text)
            if section_date in allowed_dates:
                current_row = date_section.find_parent('tr').find_next_sibling('tr')
                while current_row and not current_row.find('td', {'class': 'tableh2'}):
                    entry = current_row.find('td', {'class': 'tableb'})
                    if entry:
                        location_tag = entry.find('p', {'class': 'location-name'})
                        link_tag = entry.find('a', href=True)
                        if location_tag and link_tag:
                            location_text = re.sub(r'\s+', ' ', location_tag.get_text(strip=True))
                            location, hours = parse_location_hours(location_text)
                            name_phone = link_tag.get_text(strip=True)
                            name, phone = parse_name_phone(name_phone)
                            address = fetch_pharmacy_address(f"{GUIDE_BASE_URL}{link_tag['href']}")
                            translations = get_translations(name, location, address, city_name)
                            pharmacies.append({
                                'city': translations['city'],
                                'name': translations['name'],
                                'location': translations['location'],
                                'phone': phone,
                                'hours': hours if hours else "24h/24h",
                                'address': translations['address'],
                                'maps': translations['maps']
                            })
                    current_row = current_row.find_next_sibling('tr')
                if pharmacies:
                    return pharmacies # Stop early if we successfully grabbed the active block
        except Exception:
            continue

    # Fallback if no date sections are matched
    if not pharmacies:
        entries = soup.find_all('td', {'class': 'tableb'})
        for entry in entries:
            location_tag = entry.find('p', {'class': 'location-name'})
            link_tag = entry.find('a', href=True)
            if location_tag and link_tag:
                location_text = re.sub(r'\s+', ' ', location_tag.get_text(strip=True))
                location, hours = parse_location_hours(location_text)
                name_phone = link_tag.get_text(strip=True)
                name, phone = parse_name_phone(name_phone)
                address = fetch_pharmacy_address(f"{GUIDE_BASE_URL}{link_tag['href']}")
                translations = get_translations(name, location, address, city_name)
                pharm_data = {
                    'city': translations['city'],
                    'name': translations['name'],
                    'location': translations['location'],
                    'phone': phone,
                    'hours': hours if hours else "24h/24h",
                    'address': translations['address'],
                    'maps': translations['maps']
                }
                if pharm_data not in pharmacies:
                    pharmacies.append(pharm_data)
                    
    return pharmacies

def get_translations(name, location, address, city_name):
    location = re.sub(r'\(\d+\)', '', location).strip()
    pharmacy_trans = translate_field('pharmacy', name)
    location_trans = translate_field('location', location)
    city_trans = translate_field('city', city_name)
    address_fr = address
    address_en = translate_field('address', address)['en']
    address_ar = translate_field('address', address)['ar']
    map_links = generate_maps_links(pharmacy_trans['fr'], city_trans['fr'])
    return {
        'name': pharmacy_trans, 'location': location_trans, 'city': city_trans,
        'address': {'fr': address_fr, 'en': address_en, 'ar': address_ar},
        'maps': {"message": {"fr": "Cliquez pour obtenir l'itinéraire sur:", "en": "Click to get directions on:", "ar": "انقر للحصول على الاتجاهات على:"}, 'links': map_links}
    }

def scrape_lematin():
    result = []
    print("Collecting pharmacy links from LeMatin...")
    links = get_lematin_pharmacy_links()
    print(f"Found {len(links)} pharmacies on LeMatin. Starting scraping...")
    for i, link_info in enumerate(links, 1):
        pharmacy_data = parse_lematin_pharmacy(link_info['url'], link_info['shift'])
        if pharmacy_data:
            result.append(pharmacy_data)
        time.sleep(0.5)
    return result

def scrape_guide():
    result = []
    target_date = datetime.now(pytz.timezone('Africa/Casablanca')).date()
    print(f"\nFetching pharmacies from GuidePharmacie for: {target_date.strftime('%d/%m/%Y')}...")
    
    for city in GUIDE_CITIES_BASE:
        city_name = city.capitalize()
        print(f"Checking {city_name}...")
        
        # Test all URL formats
        paths_to_try = [
            f"/pharmacies-de-garde/{city}.html",
            f"/pharmacies-de-garde/nuit/{city}.html",
            f"/pharmacies-de-garde/week/{city}.html"
        ]
        
        pharmacies = []
        for path in paths_to_try:
            city_url = f"{GUIDE_BASE_URL}{path}"
            try:
                response = requests.get(city_url, headers=GLOBAL_HEADERS, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    pharmacies = extract_guide_pharmacy_data(soup, city_name, target_date)
                    if pharmacies:
                        print(f"-> Succès : {len(pharmacies)} pharmacies trouvées pour {city_name} via {path}")
                        break
            except requests.RequestException as e:
                print(f"Error fetching route {city_url}: {e}")
                continue
                
        if not pharmacies:
            print(f"-> Échec : Aucune pharmacie trouvée pour {city_name}.")
            
        result.extend(pharmacies)
        time.sleep(1)
    return result

def main():
    all_pharmacies = {
         "date": datetime.now(pytz.timezone('Africa/Casablanca')).date().isoformat(),
        "sources": {
            "lematin": {"pharmacies": scrape_lematin()},
            "guide": {"pharmacies": scrape_guide()}
        }
    }
    
    all_pharmacies["total_pharmacies"] = (
        len(all_pharmacies["sources"]["lematin"]["pharmacies"]) +
        len(all_pharmacies["sources"]["guide"]["pharmacies"])
    )
    
    # WE NOW SAVE TO THE EXACT STATIC FILENAME
    filename = 'pharmacyData.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_pharmacies, f, ensure_ascii=False, indent=2)
    
    print(f"\nData has been saved to {filename}")
    print(f"Total pharmacies found: {all_pharmacies['total_pharmacies']}")
    print(f"- LeMatin: {len(all_pharmacies['sources']['lematin']['pharmacies'])}")
    print(f"- GuidePharmacie: {len(all_pharmacies['sources']['guide']['pharmacies'])}")

if __name__ == "__main__":
    main()
