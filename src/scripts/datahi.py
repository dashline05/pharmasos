import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from urllib.parse import urljoin, urlparse, quote
import re
import json
import time
import pytz

# --- Logique de date ---
tz = pytz.timezone('Africa/Casablanca')
now = datetime.now(tz)
date_actuelle = now.date() # Ex: 2025-11-08 (Samedi)

# Calculer le Lundi de la semaine actuelle (Aujourd'hui - jours écoulés depuis Lundi)
lundi_de_la_semaine_actuelle = date_actuelle - timedelta(days=date_actuelle.weekday())

# Formater la chaîne de date pour l'URL (toujours Lundi)
date_lundi_str = lundi_de_la_semaine_actuelle.strftime('%Y-%m-%d') # Ex: "2025-11-03"
# --- Fin Logique de date ---


# Base URLs
LEMATIN_BASE_URL = "https://lematin.ma" # Corrigé
GUIDE_BASE_URL = "https://www.guidepharmacies.ma"

# URLs for both sources
LEMATIN_URLS = [
    "https://lematin.ma/pharmacie-garde-casablanca/jour/ain-chock",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/ain-sebaa",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/al-azhar-panorama",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/al-fida",
    "https://lematin.ma/pharmacie-garde-casablanca/jour/annasi",

]

# Configuration des villes pour GuidePharmacie
GUIDE_CITY_CONFIG = [
    {
        # On charge TOUJOURS la page du Lundi
        "path": f"/pharmacies-de-garde/rabat.html?date={date_lundi_str}",
        # Mais on cherche la date du jour actuel (ex: Samedi 8)
        "target_date_obj": date_actuelle
    },
    {
        "path": f"/pharmacies-de-garde/sale.html?date={date_lundi_str}",
        "target_date_obj": date_actuelle
    },
    {
        "path": f"/pharmacies-de-garde/temara.html?date={date_lundi_str}",
        "target_date_obj": date_actuelle
    },
    {
        "path": f"/pharmacies-de-garde/ain-aouda.html?date={date_lundi_str}",
        "target_date_obj": date_actuelle
    }
]


# Translation dictionaries
month_mapping = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

city_translations = {
    'Rabat': {'fr': 'Rabat', 'en': 'Rabat', 'ar': 'الرباط'},
    'Sale': {'fr': 'Sale', 'en': 'Sale', 'ar': 'سلا'},
    'Temara': {'fr': 'Temara', 'en': 'Temara', 'ar': 'تمارة'},
    'Casablanca': {'fr': 'Casablanca', 'en': 'Casablanca', 'ar': 'الدار البيضاء'},
    'Marrakech': {'fr': 'Marrakech', 'en': 'Marrakech', 'ar': 'مراكش'}
}

pharmacy_translations = {
    'Pharmacie RELAIS DES MEDECINS': {'fr': 'Pharmacie RELAIS DES MEDECINS', 'en': 'Pharmacy RELAIS DES DOCTORS', 'ar': 'صيدلية راليه دي ميديسين'},
    'Pharmacie YAACOUB EL MANSOUR': {'fr': 'Pharmacie YAACOUB EL MANSOUR', 'en': 'YAACOUB EL MANSOUR Pharmacy', 'ar': 'صيدلية يعقوب المنصور'},
    'Pharmacie KARIOUN': {'fr': 'Pharmacie KARIOUN', 'en': 'KARIOUN Pharmacy', 'ar': 'صيدلية قاريون'},
    'Pharmacie AL AMANA': {'fr': 'Pharmacie AL AMANA', 'en': 'AL AMANA Pharmacy', 'ar': 'صيدلية الامانة'},
    'Pharmacie ISWANE': {'fr': 'Pharmacie ISWANE', 'en': 'ISWANE Pharmacy', 'ar': 'صيدلية إيسوان'},
    'Pharmacie DU THEATRE': {'fr': 'Pharmacie DU THEATRE', 'en': 'THEATER Pharmacy', 'ar': 'صيدلية المسرح'},
    'Pharmacie AL JAZAA': {'fr': 'Pharmacie AL JAZAA', 'en': 'AL JAZAA Pharmacy', 'ar': 'صيدلية الجزاء'},
    'Pharmacie ABI HOURAYRA': {'fr': 'Pharmacie ABI HOURAYRA', 'en': 'ABI HOURAYRA Pharmacy', 'ar': 'صيدلية أبي هريرة'},
    'Pharmacie ABTAL': {'fr': 'Pharmacie ABTAL', 'en': 'ABTAL Pharmacy', 'ar': 'صيدلية ابطال'},
    'PHARMACIE DE L\'AVENIR': {'fr': 'PHARMACIE DE L\'AVENIR', 'en': 'PHARMACY OF THE FUTURE', 'ar': 'صيدلية المستقبل'},
    'PHARMACIE DE L\'ESPERANCE': {'fr': 'PHARMACIE DE L\'ESPERANCE', 'en': 'PHARMACY OF ESPERANCE', 'ar': 'صيدلية الترجي'},
    'PHARMACIE DU LITTORAL': {'fr': 'PHARMACIE DU LITTORAL', 'en': 'LITTORAL PHARMACY', 'ar': 'الصيدلية الساحلية'},
    'PHARMACIE DU LOUVRE': {'fr': 'PHARMACIE DU LOUVRE', 'en': 'LOUVRE PHARMACY', 'ar': 'صيدلية اللوفر'},
    'PHARMACIE DU LYCEE': {'fr': 'PHARMACIE DU LYCEE', 'en': 'HIGH SCHOOL PHARMACY', 'ar': 'صيدلية المدرسة الثانوية'},
    'PHARMACIE DU LYCEE CHAWKI': {'fr': 'PHARMACIE DU LYCEE CHAWKI', 'en': 'CHAWKI LYCEE PHARMACY', 'ar': 'صيدلية شوقي ليسيه'},
    'PHARMACIE DU LYS': {'fr': 'PHARMACIE DU LYS', 'en': 'LYS PHARMACY', 'ar': 'صيدلية ليس'},
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
    'M\'Hamid': {'fr': 'M\'Hamid', 'en': 'M\'Hamid', 'ar': 'مْحاميد'},
    'Medina': {'fr': 'Medina', 'en': 'Medina', 'ar': 'المدينة'},
    'Sidi Ghanem': {'fr': 'Sidi Ghanem', 'en': 'Sidi Ghanem', 'ar': 'سيدي غانم'},
    'Sidi Youssef Ben Ali': {'fr': 'Sidi Youssef Ben Ali', 'en': 'Sidi Youssef Ben Ali', 'ar': 'سيدي يوسف بن علي'},
    'Targa': {'fr': 'Targa', 'en': 'Targa', 'ar': 'تارڭا'}
}

address_translations = {
    "Rue": {'en': 'Street', 'ar': 'شارع'},
    "Avenue": {'en': 'Avenue', 'ar': 'شارع'},
    "Av": {'en': 'Ave', 'ar': 'شارع'},  # Abbreviation expanded
    "Boulevard": {'en': 'Boulevard', 'ar': 'شارع'},
    "Bloc": {'en': 'Block', 'ar': 'بلوك'},
    "Secteur": {'en': 'Sector', 'ar': 'قطاع'},
    "Résidence": {'en': 'Residence', 'ar': 'إقامة'},
    "Centre": {'en': 'Center', 'ar': 'مركز'},
    "commercial": {'en': 'Commercial', 'ar': 'تجاري'},
    "Angle": {'en': 'Corner', 'ar': 'زاوية'},
    "En face": {'en': 'Opposite', 'ar': 'مقابل'},
    "Prés": {'en': 'Near', 'ar': 'قرب'},
    "du": {'en': 'of the', 'ar': 'من'},  # Prepositions/contextual
    "de": {'en': 'of', 'ar': 'من'},
    "la": {'en': 'the', 'ar': 'ال'},     # Articles
    "le": {'en': 'the', 'ar': 'ال'},
    "Al": {'en': 'Al', 'ar': 'ال'},      # Retained as part of names
    "et": {'en': 'and', 'ar': 'و'},
    "Hay": {'en': 'Neighborhood', 'ar': 'حي'},
    "Imm": {'en': 'Building', 'ar': 'عمارة'},
    "Lotissement": {'en': 'Subdivision', 'ar': 'تجزئة'},
    "Villa": {'en': 'Villa', 'ar': 'فيلا'},
    "Douar": {'en': 'Douar', 'ar': 'دوار'},  # Retained (cultural term)
    "Centre dentaire": {'en': 'Dental Center', 'ar': 'مركز طب الأسنان'},
    "gare routiere": {'en': 'Bus Station', 'ar': 'محطة الحافلات'},
    "Rond-Point": {'en': 'Roundabout', 'ar': 'الدوار'},
}


hours_translations = {
    "Day et Nuit": {
        "fr": "24h/24h",
        "en": "24h/24h",
        "ar": "24h/24h"
    },
    "Day": {
        "fr": "09h00 - 00h00",
        "en": "09h00 - 00h00",
        "ar": "09h00 - 00h00"
    },
    "Nuit": {
        "fr": "24h/24h",
        "en": "24h/24h",
        "ar": "24h/24h"
    },
    "Unknown": {
        "fr": "aucune",
        "en": "none",
        "ar": "غير متوفر"
    }
}

def normalize_pharmacy_name(name):
    """Normalize pharmacy name by removing extra spaces and standardizing format"""
    # Remove multiple spaces and trim
    name = ' '.join(name.split())
    # Remove "Pharmacie " or "PHARMACIE " prefix if present
    if name.lower().startswith('pharmacie '):
        name = name[10:]
    return name.strip()

def get_pharmacy_translation(name, translations):
    """Get translation for a pharmacy name, handling different format variations"""
    # Normalize the input name
    normalized_name = normalize_pharmacy_name(name)
    
    # Try different format combinations
    possible_keys = [
        f"Pharmacie {normalized_name}",
        f"PHARMACIE {normalized_name}",
        normalized_name
    ]
    
    for key in possible_keys:
        if key in translations:
            return translations[key]
            
    # If exact match not found, try case-insensitive search
    normalized_name_lower = normalized_name.lower()
    for key in translations:
        if normalize_pharmacy_name(key).lower() == normalized_name_lower:
            return translations[key]
            
    # If still not found, return original name in all fields
    return {'fr': name, 'en': name, 'ar': name}

def translate_field(field, value):
    """Translate a field value using the translation dictionaries."""
    translation_map = {
        'city': city_translations,
        'pharmacy': pharmacy_translations,
        'location': location_translations,
        'address': address_translations,
        'hours': hours_translations
    }
    
    translations = translation_map.get(field, {})
    
    # Special handling for pharmacy names
    if field == 'pharmacy':
        return get_pharmacy_translation(value, translations)
    
    # Handle other fields as before
    if value in translations:
        return translations[value]
    else:
        return {"fr": value, "en": value, "ar": value}

def generate_maps_links(name, city):
    """Generate map links using pharmacy name and city only"""
    query = f"{name} {city}"
    encoded_query = quote(query)
    return {
        "google_maps": f"https://www.google.com/maps/search/?api=1&query={encoded_query}",
        "waze": f"https://www.waze.com/ul?q={encoded_query}&navigate=yes",
        "apple_maps": f"http://maps.apple.com/?q={encoded_query}"
    }

# LeMatin scraping functions
def get_lematin_pharmacy_links():
    """Get pharmacy links from LeMatin"""
    pharmacy_links = []
    for url in LEMATIN_URLS:
        try:
            # Determine shift from URL
            shift = 'jour' if '/jour/' in url else 'nuit' if '/nuit/' in url else 'unknown'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            records = soup.select('div.pharmacies div.ph-record')
            
            for record in records:
                link = record.select_one('div.ph-name a')['href']
                full_url = urljoin(LEMATIN_BASE_URL, link)
                pharmacy_links.append({'url': full_url, 'shift': shift})
            
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
    return pharmacy_links

def parse_lematin_pharmacy(url, shift):
    """Parse individual pharmacy from LeMatin"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Determine hours key
        hours_key = 'Day' if shift == 'jour' else 'Nuit' if shift == 'nuit' else 'Unknown'
        
        data = {
            "city": {"fr": "", "en": "", "ar": ""},
            "name": {"fr": "", "en": "", "ar": ""},
            "location": {"fr": "", "en": "", "ar": ""},
            "phone": None,
            "hours": translate_field('hours', hours_key),
            "address": {"fr": "", "en": "", "ar": ""},
            "maps": {
                "message": {
                    # --- CORRECTION SYNTAXERROR ---
                    "fr": "Cliquez pour obtenir l'itinéraire sur:",
                    "en": "Click to get directions on:",
                    "ar": "انقر للحصول على الاتجاهات على:"
                },
                "links": {}
            }
        }

        # Extract pharmacy details
        name_tag = soup.select_one('.record.pharmacy-name')
        if name_tag:
            raw_parts = [text.strip() for text in name_tag.find_all(text=True, recursive=True) 
                        if "Modifier ou compléter" not in text]
            raw_name = " ".join(raw_parts).strip()
            data["name"] = translate_field('pharmacy', raw_name)

        # Extract other details
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

        # Generate maps links
        if data["name"]["fr"] and data["city"]["fr"]:
            data["maps"]["links"] = generate_maps_links(
                data["name"]["fr"], 
                data["city"]["fr"]
            )

        return data
    except Exception as e:
        print(f"Error parsing {url}: {str(e)}")
        return None

# Guide Pharmacies scraping functions
def get_city_name(url):
    """Extract city name from URL"""
    path = urlparse(url).path
    return path.split('/')[-1].replace('.html', '').capitalize()

def parse_french_date(date_str):
    """Parse French date string"""
    parts = re.split(r'\s+', date_str.strip()) # ex: "Samedi 08 Novembre 2025"
    day = int(parts[1])
    month = month_mapping[parts[2].lower()]
    year = int(parts[3])
    return datetime(year, month, day).date()

def parse_location_hours(text):
    """Parse location and hours from text"""
    text = text.strip()
    if not text:
        return '', ''
    
    text = re.sub(r'\(\d+\)', '', text).strip()
    
    hour_patterns = [
        r'24h/24h',
        r'\d+h à \d+h',
        r'\d+h à \d+h:\d+'
    ]
    
    hours = ''
    for pattern in hour_patterns:
        match = re.search(pattern, text)
        if match:
            hours = match.group(0).strip()
            text = text.replace(hours, '').strip()
            break
    
    if not hours and '(' in text:
        parts = text.split('(', 1)
        if len(parts) > 1:
            location = parts[0].strip()
            hours = parts[1].replace(')', '').strip()
        else:
            location = text.strip()
    else:
        location = text.strip()
    
    return location, hours

def parse_name_phone(text):
    """Parse name and phone from text"""
    parts = text.split(' - ', 1)
    return parts[0].strip(), parts[1].strip() if len(parts) > 1 else ''

def fetch_pharmacy_address(url):
    """Fetch pharmacy address from detail page"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        description_div = soup.find('div', {'class': 'eb-description-details'})
        
        if description_div:
            address_paragraphs = description_div.find_all(
                'p', 
                style=re.compile(r'text-align:\s*center', re.IGNORECASE)
            )
            address_lines = [
                p.get_text(strip=True) 
                for p in address_paragraphs 
                if 'Tél:' not in p.get_text()
            ]
            return ' | '.join(address_lines) or "Address not found"
        return "Address not found"
    except Exception as e:
        print(f"Error fetching address: {e}")
        return "Address unavailable"

def extract_guide_pharmacy_data(soup, city_name, target_date):
    """Extract pharmacy data from Guide Pharmacies"""
    pharmacies = []
    date_sections = soup.find_all('td', {'class': 'tableh2'})

    for date_section in date_sections:
        date_text = date_section.get_text(strip=True)
        try:
            section_date = parse_french_date(date_text)
            
            # Vérifie si la date de la section (ex: "Samedi 08 Novembre")
            # correspond à la date cible (la date du jour)
            if section_date == target_date:
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
                                'hours': hours,
                                'address': translations['address'],
                                'maps': translations['maps']
                            })
                    
                    current_row = current_row.find_next_sibling('tr')
                break # Arrête de chercher une fois la bonne date trouvée
        except (KeyError, ValueError, IndexError):
            # Continue si la date n'est pas parsable (ex: 'Pharmacies de garde')
            continue
    
    return pharmacies

def get_translations(name, location, address, city_name):
    """Get translations for all fields"""
    location = re.sub(r'\(\d+\)', '', location).strip()
    
    pharmacy_trans = translate_field('pharmacy', name)
    location_trans = translate_field('location', location)
    city_trans = translate_field('city', city_name)
    
    address_fr = address
    address_en = translate_field('address', address)['en']
    address_ar = translate_field('address', address)['ar']
    
    map_links = generate_maps_links(pharmacy_trans['fr'], city_trans['fr'])
    
    return {
        'name': pharmacy_trans,
        'location': location_trans,
        'city': city_trans,
        'address': {
            'fr': address_fr,
            'en': address_en,
            'ar': address_ar
        },
        'maps': {
            'message': {
                # --- CORRECTION SYNTAXERROR ---
                "fr": "Cliquez pour obtenir l'itinéraire sur:",
                "en": "Click to get directions on:",
                "ar": "انقر للحصول على الاتجاهات على:"
            },
            'links': map_links
        }
    }

def scrape_lematin():
    """Scrape pharmacies from LeMatin"""
    result = []
    print("Collecting pharmacy links from LeMatin...")
    links = get_lematin_pharmacy_links()
    
    print(f"Found {len(links)} pharmacies on LeMatin. Starting scraping...")
    for i, link_info in enumerate(links, 1):
        print(f"Processing LeMatin pharmacy {i}/{len(links)}")
        pharmacy_data = parse_lematin_pharmacy(link_info['url'], link_info['shift'])
        if pharmacy_data:
            result.append(pharmacy_data)
        time.sleep(1)
    
    return result

def scrape_guide():
    """Scrape pharmacies from Guide Pharmacies"""
    result = []
    
    print(f"\nFetching pharmacies from GuidePharmacie...")
    
    # Boucle sur la configuration (qui contient URL du Lundi et date cible du jour actuel)
    for config in GUIDE_CITY_CONFIG:
        city_path = config["path"]
        target_date = config["target_date_obj"]  # Date cible (ex: Samedi 8)
        
        city_url = f"{GUIDE_BASE_URL}{city_path}" # URL (ex: Lundi 3)
        city_name = get_city_name(city_url)
        
        print(f"Checking {city_name} (Date cible: {target_date.strftime('%Y-%m-%d')}) using URL: {city_url}")
        
        try:
            response = requests.get(city_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Passe la date cible correcte (Samedi 8) à l'extracteur
            pharmacies = extract_guide_pharmacy_data(soup, city_name, target_date)
            result.extend(pharmacies)
            
        except requests.RequestException as e:
            print(f"Error fetching {city_name} page: {e}")
            continue
            
    return result

def main():
    """Main function to scrape both sources and combine results"""
    all_pharmacies = {
         "date": datetime.now(pytz.timezone('Africa/Casablanca')).date().isoformat(),
        "sources": {
            "lematin": {
                "pharmacies": scrape_lematin()
            },
            "guide": {
                "pharmacies": scrape_guide()
            }
        }
    }
    
    # Add summary statistics
    all_pharmacies["total_pharmacies"] = (
        len(all_pharmacies["sources"]["lematin"]["pharmacies"]) +
        len(all_pharmacies["sources"]["guide"]["pharmacies"])
    )
    
    # Save combined results
    filename = f'pharmacies_{date_actuelle.isoformat()}.json' # Utilise date_actuelle
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_pharmacies, f, ensure_ascii=False, indent=2)
    
    print(f"\nData has been saved to {filename}")
    print(f"Total pharmacies found: {all_pharmacies['total_pharmacies']}")
    print(f"- LeMatin: {len(all_pharmacies['sources']['lematin']['pharmacies'])}")
    print(f"- GuidePharmacie: {len(all_pharmacies['sources']['guide']['pharmacies'])}")

if __name__ == "__main__":
    main()
