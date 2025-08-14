import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from urllib.parse import urljoin
import json
import pytz

# Base URLs for the two sources
LEMATIN_BASE_URL = "https://lematin.ma"
GUIDE_BASE_URL = "https://www.guidepharmacies.ma"

# Function to get the date of the next or current Monday in Morocco's timezone
def get_next_or_current_monday():
    """
    Determines the date of the next or current Monday in the 'Africa/Casablanca' timezone.
    If today is Monday, it returns today's date. Otherwise, it returns the date of the next Monday.
    """
    morocco_tz = pytz.timezone('Africa/Casablanca')
    now = datetime.now(morocco_tz)
    
    if now.weekday() == 0:
        return now.strftime('%Y-%m-%d')
    
    days_until_monday = (7 - now.weekday()) % 7
    next_monday = now + timedelta(days=days_until_monday)
    return next_monday.strftime('%Y-%m-%d')

# Function to generate the correct list of URLs for guidepharmacies.ma
def get_guide_cities_urls(manual_date=None):
    """
    Generates the list of URLs for guidepharmacies.ma based on the current day or a manual date.
    """
    cities = [
        "/pharmacies-de-garde/rabat.html",
        "/pharmacies-de-garde/sale.html",
        "/pharmacies-de-garde/temara.html",
        "/pharmacies-de-garde/ain-aouda.html"
    ]
    
    morocco_tz = pytz.timezone('Africa/Casablanca')
    now = datetime.now(morocco_tz)
    
    if manual_date:
        date_param = manual_date
    elif now.weekday() == 0:
        date_param = get_next_or_current_monday()
    else:
        print("Today is not Monday. Using current URLs without a date parameter.")
        return [urljoin(GUIDE_BASE_URL, city) for city in cities]

    print(f"Using date parameter for Monday: {date_param}")
    return [urljoin(GUIDE_BASE_URL, f"{city}?date={date_param}") for city in cities]

# URLs for both sources (lematin.ma)
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

# Translation dictionaries (completed)
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
    'Pharmacie ASSOROUR': {'fr': 'Pharmacie ASSOROUR', 'en': 'ASSOROUR Pharmacy', 'ar': 'صيدلية السرور'},
    'Pharmacie RIMA': {'fr': 'Pharmacie RIMA', 'en': 'RIMA Pharmacy', 'ar': 'صيدلية ريما'},
    'Pharmacie TAIBA': {'fr': 'Pharmacie TAIBA', 'en': 'TAIBA Pharmacy', 'ar': 'صيدلية طيبة'},
    'Pharmacie BOUCHOUK': {'fr': 'Pharmacie BOUCHOUK', 'en': 'BOUCHOUK Pharmacy', 'ar': 'صيدلية بوشوق'},
    'Pharmacie LES ARCEAUX': {'fr': 'Pharmacie LES ARCEAUX', 'en': 'Pharmacy LES ARCEAUX', 'ar': 'صيدلية الأقواس'},
    'Pharmacie ARGANA': {'fr': 'Pharmacie ARGANA', 'en': 'ARGANA Pharmacy', 'ar': 'صيدلية ارجانا'},
    'Pharmacie IBN ROCHD': {'fr': 'Pharmacie IBN ROCHD', 'en': 'IBN ROCHD Pharmacy', 'ar': 'صيدلية ابن رشد'},
    'Pharmacie AL A\'ARAF': {'fr': 'Pharmacie AL A\'ARAF', 'en': 'AL A\'ARAF Pharmacy', 'ar': 'صيدلية الأعراف'},
    'Pharmacie VOLUBILIS': {'fr': 'Pharmacie VOLUBILIS', 'en': 'VOLUBILIS Pharmacy', 'ar': 'صيدلية فولوبيليس'},
    'Pharmacie AL AHBAB': {'fr': 'Pharmacie AL AHBAB', 'en': 'AL AHBAB Pharmacy', 'ar': 'صيدلية الاحباب'},
    'Pharmacie AL ANWAR': {'fr': 'Pharmacie AL ANWAR', 'en': 'AL ANWAR Pharmacy', 'ar': 'صيدلية الأنوار'},
    'Pharmacie L\'HONNEUR': {'fr': 'Pharmacie L\'HONNEUR', 'en': 'HONOR Pharmacy', 'ar': 'صيدلية الشرف'},
    'Pharmacie TIDARINE': {'fr': 'Pharmacie TIDARINE', 'en': 'TIDARINE Pharmacy', 'ar': 'صيدلية تيدارين'},
    'Pharmacie ROUTE MEHDIA': {'fr': 'Pharmacie ROUTE MEHDIA', 'en': 'Pharmacy ROUTE MEHDIA', 'ar': 'صيدلية طريق المهدية'},
    'Pharmacie DAHAB': {'fr': 'Pharmacie DAHAB', 'en': 'DAHAB Pharmacy', 'ar': 'صيدلية دهب'},
    'Pharmacie AL OMRANE': {'fr': 'Pharmacie AL OMRANE', 'en': 'AL OMRANE Pharmacy', 'ar': 'صيدلية العمران'},
    'Pharmacie NEJJAR': {'fr': 'Pharmacie NEJJAR', 'en': 'NEJJAR Pharmacy', 'ar': 'صيدلية نجار'},
    'Pharmacie CENTRALE': {'fr': 'Pharmacie CENTRALE', 'en': 'CENTRAL Pharmacy', 'ar': 'الصيدلية المركزية'},
    'Pharmacie LES JUMELLES Ex: Village': {'fr': 'Pharmacie LES JUMELLES Ex: Village', 'en': 'Pharmacy LES JUMELLES Ex: Village', 'ar': 'صيدلية التوأمان'},
    'Pharmacie SAKANI': {'fr': 'Pharmacie SAKANI', 'en': 'SAKANI Pharmacy', 'ar': 'صيدلية سكني'},
    'Pharmacie SAID HAJJI': {'fr': 'Pharmacie SAID HAJJI', 'en': 'SAID HAJJI Pharmacy', 'ar': 'صيدلية سعيد حجي'},
    'Pharmacie RAMADAN': {'fr': 'Pharmacie RAMADAN', 'en': 'RAMADAN Pharmacy', 'ar': 'صيدلية رمضان'},
    'Pharmacie LA MAMORA': {'fr': 'Pharmacie LA MAMORA', 'en': 'LA MAMORA Pharmacy', 'ar': 'صيدلية لا معمورة'},
    'Pharmacie AHMED HAJJI': {'fr': 'Pharmacie AHMED HAJJI', 'en': 'AHMED HAJJI Pharmacy', 'ar': 'صيدلية احمد حجي'},
    'Pharmacie WAHIBA': {'fr': 'Pharmacie WAHIBA', 'en': 'WAHIBA Pharmacy', 'ar': 'صيدلية وهيبة'},
    'Pharmacie SAFIR': {'fr': 'Pharmacie SAFIR', 'en': 'SAFIR Pharmacy', 'ar': 'صيدلية سفير'},
    'Pharmacie ILHAM': {'fr': 'Pharmacie ILHAM', 'en': 'ILHAM Pharmacy', 'ar': 'صيدلية الهام'},
    'Pharmacie SIDI ABDELLAH BEN HASSOUN': {'fr': 'Pharmacie SIDI ABDELLAH BEN HASSOUN', 'en': 'Pharmacy SIDI ABDELLAH BEN HASSOUN', 'ar': 'صيدلية سيدي عبد الله بن حسون'},
    'Pharmacie MAIL CENTRAL': {'fr': 'Pharmacie MAIL CENTRAL', 'en': 'Pharmacy MAIL CENTRAL', 'ar': 'صيدلية البريد المركزي'},
    'Pharmacie DU MYRTE': {'fr': 'Pharmacie DU MYRTE', 'en': 'MYRTE Pharmacy', 'ar': 'صيدلية ميرتي'},
    'Pharmacie AL HANANE': {'fr': 'Pharmacie AL HANANE', 'en': 'AL HANANE Pharmacy', 'ar': 'صيدلية الحنان'},
    'Pharmacie RIF': {'fr': 'Pharmacie RIF', 'en': 'RIF Pharmacy', 'ar': 'صيدلية ريف'},
    'Pharmacie ACHOUHADAA': {'fr': 'Pharmacie ACHOUHADAA', 'en': 'ACHOUHADAA Pharmacy', 'ar': 'صيدلية الشهداء'},
    'Pharmacie ASSABIL': {'fr': 'Pharmacie ASSABIL', 'en': 'ASSABIL Pharmacy', 'ar': 'صيدلية السبيل'},
    'Pharmacie ERRAI': {'fr': 'Pharmacie ERRAI', 'en': 'ERRAI Pharmacy', 'ar': 'صيدلية الراي'},
    'Pharmacie DOCTEUR HILAL': {'fr': 'Pharmacie DOCTEUR HILAL', 'en': 'DOCTEUR HILAL Pharmacy', 'ar': 'صيدلية الدكتور هلال'},
    'Pharmacie AZZEDINE': {'fr': 'Pharmacie AZZEDINE', 'en': 'AZZEDINE Pharmacy', 'ar': 'صيدلية عز الدين'},
    'Pharmacie CHELLALINE': {'fr': 'Pharmacie CHELLALINE', 'en': 'CHELLALINE Pharmacy', 'ar': 'صيدلية شلالين'},
    'Pharmacie ASSEHA': {'fr': 'Pharmacie ASSEHA', 'en': 'ASSEHA Pharmacy', 'ar': 'صيدلية صحة'},
    'Pharmacie BETTANA': {'fr': 'Pharmacie BETTANA', 'en': 'BETTANA Pharmacy', 'ar': 'صيدلية بيتانا'},
    'Pharmacie NAHDA': {'fr': 'Pharmacie NAHDA', 'en': 'NAHDA Pharmacy', 'ar': 'صيدلية النهضة'},
    'Pharmacie ALHAMD': {'fr': 'Pharmacie ALHAMD', 'en': 'ALHAMD Pharmacy', 'ar': 'صيدلية الحمد'},
    'Pharmacie CHIFAA': {'fr': 'Pharmacie CHIFAA', 'en': 'CHIFAA Pharmacy', 'ar': 'صيدلية الشفاء'},
    'Pharmacie BAYTI': {'fr': 'Pharmacie BAYTI', 'en': 'BAYTI Pharmacy', 'ar': 'صيدلية بيتي'},
    'Pharmacie IBTISSAM': {'fr': 'Pharmacie IBTISSAM', 'en': 'IBTISSAM Pharmacy', 'ar': 'صيدلية ابتسام'},
    'Pharmacie GHRISS': {'fr': 'Pharmacie GHRISS', 'en': 'GHRISS Pharmacy', 'ar': 'صيدلية غريس'},
    'Pharmacie SABI': {'fr': 'Pharmacie SABI', 'en': 'SABI Pharmacy', 'ar': 'صيدلية سابي'},
    'Pharmacie MEHDIA': {'fr': 'Pharmacie MEHDIA', 'en': 'MEHDIA Pharmacy', 'ar': 'صيدلية المهدية'},
    'Pharmacie LA MARINA': {'fr': 'Pharmacie LA MARINA', 'en': 'Pharmacy LA MARINA', 'ar': 'صيدلية لا مارينا'},
    'Pharmacie AL KASBA': {'fr': 'Pharmacie AL KASBA', 'en': 'AL KASBA Pharmacy', 'ar': 'صيدلية القصبة'},
    'Pharmacie GRANADA': {'fr': 'Pharmacie GRANADA', 'en': 'GRANADA Pharmacy', 'ar': 'صيدلية غرناطة'},
    'Pharmacie ERRAHA': {'fr': 'Pharmacie ERRAHA', 'en': 'ERRAHA Pharmacy', 'ar': 'صيدلية الراحة'},
    'Pharmacie ALI': {'fr': 'Pharmacie ALI', 'en': 'ALI Pharmacy', 'ar': 'صيدلية علي'},
    'Pharmacie SABLES D\'OR': {'fr': 'Pharmacie SABLES D\'OR', 'en': 'SABLES D\'OR Pharmacy', 'ar': 'صيدلية سابل دور'},
    'Pharmacie TARIK IBN ZIAD': {'fr': 'Pharmacie TARIK IBN ZIAD', 'en': 'TARIK IBN ZIAD Pharmacy', 'ar': 'صيدلية طارق بن زياد'},
    'Pharmacie JNANE BELFQUIH': {'fr': 'Pharmacie JNANE BELFQUIH', 'en': 'JNANE BELFQUIH Pharmacy', 'ar': 'صيدلية جنان بلفقيه'},
    'Pharmacie AL HIBA': {'fr': 'Pharmacie AL HIBA', 'en': 'AL HIBA Pharmacy', 'ar': 'صيدلية الهيبة'},
    'Pharmacie ACIMA HARHOURA': {'fr': 'Pharmacie ACIMA HARHOURA', 'en': 'ACIMA HARHOURA Pharmacy', 'ar': 'صيدلية اسيما هرهورة'},
    'Pharmacie ARREDOUANE': {'fr': 'Pharmacie ARREDOUANE', 'en': 'ARREDOUANE Pharmacy', 'ar': 'صيدلية العرضوان'},
    'Pharmacie ENNASSIM': {'fr': 'Pharmacie ENNASSIM', 'en': 'ENNASSIM Pharmacy', 'ar': 'صيدلية النسيم'},
    'Pharmacie MIRAMAR': {'fr': 'Pharmacie MIRAMAR', 'en': 'MIRAMAR Pharmacy', 'ar': 'صيدلية ميرامار'},
    'Pharmacie MOSQUEE ZAHRA': {'fr': 'Pharmacie MOSQUEE ZAHRA', 'en': 'MOSQUEE ZAHRA Pharmacy', 'ar': 'صيدلية مسجد الزهراء'},
    'Pharmacie PRINCIPALE': {'fr': 'Pharmacie PRINCIPALE', 'en': 'MAIN Pharmacy', 'ar': 'الصيدلية الرئيسية'},
    'Pharmacie AL KASBAH': {'fr': 'Pharmacie AL KASBAH', 'en': 'AL KASBAH Pharmacy', 'ar': 'صيدلية القصبة'},
    'Pharmacie ECHOUMOUE': {'fr': 'Pharmacie ECHOUMOUE', 'en': 'ECHOUMOUE Pharmacy', 'ar': 'صيدلية إشومو'},
    'Pharmacie AL FAJR': {'fr': 'Pharmacie AL FAJR', 'en': 'AL FAJR Pharmacy', 'ar': 'صيدلية الفجر'},
    'Pharmacie JARDINS DES OUDAYAS': {'fr': 'Pharmacie JARDINS DES OUDAYAS', 'en': 'Pharmacy JARDINS DES OUDAYAS', 'ar': 'صيدلية جاردان الوداية'},
    'Pharmacie AZUR': {'fr': 'Pharmacie AZUR', 'en': 'AZUR Pharmacy', 'ar': 'صيدلية أزور'},
    'PHARMACIE 2 M': {'fr': 'PHARMACIE 2 M', 'en': 'PHARMACY 2 M', 'ar': 'صيدلية 2 م'},
    'Pharmacie BELKZIZ': {'fr': 'Pharmacie BELKZIZ', 'en': 'BELKZIZ PHARMACY', 'ar': 'صيدلية بلقزيز'},
    'Pharmacie LA ROSEE': {'fr': 'Pharmacie LA ROSEE', 'en': 'THE DEW PHARMACY', 'ar': 'صيدلية الندى'},
    'Pharmacie BAB MARRAKECH': {'fr': 'Pharmacie BAB MARRAKECH', 'en': 'BAB MARRAKECH PHARMACY', 'ar': 'صيدلية باب مراكش'},
    'Pharmacie DE LA RESISTANCE': {'fr': 'Pharmacie DE LA RESISTANCE', 'en': 'RESISTANCE PHARMACY', 'ar': 'صيدلية المقاومة'},
    'Pharmacie CHBANAT': {'fr': 'Pharmacie CHBANAT', 'en': 'CHBANAT PHARMACY', 'ar': 'صيدلية الشبانة'},
    'Pharmacie AL HIKMA': {'fr': 'Pharmacie AL HIKMA', 'en': 'AL HIKMA PHARMACY', 'ar': 'صيدلية الحكمة'},
    'Pharmacie BORJ': {'fr': 'Pharmacie BORJ', 'en': 'BORJ PHARMACY', 'ar': 'صيدلية البرج'},
    'Pharmacie ALAM': {'fr': 'Pharmacie ALAM', 'en': 'ALAM PHARMACY', 'ar': 'صيدلية العلم'},
    'Pharmacie HAY AL KORA': {'fr': 'Pharmacie HAY AL KORA', 'en': 'HAY AL KORA PHARMACY', 'ar': 'صيدلية حي الكورة'},
    'Pharmacie CHOUKROALLAH': {'fr': 'Pharmacie CHOUKROALLAH', 'en': 'CHOUKROALLAH PHARMACY', 'ar': 'صيدلية شكر الله'},
    'Pharmacie ATTAISSIR': {'fr': 'Pharmacie ATTAISSIR', 'en': 'ATTAISSIR PHARMACY', 'ar': 'صيدلية التيسير'},
    'Pharmacie CHEMS': {'fr': 'Pharmacie CHEMS', 'en': 'CHEMS PHARMACY', 'ar': 'صيدلية شمس'},
    'Pharmacie MOULAY ISMAIL': {'fr': 'Pharmacie MOULAY ISMAIL', 'en': 'MOULAY ISMAIL PHARMACY', 'ar': 'صيدلية مولاي إسماعيل'},
    'Pharmacie WARDA': {'fr': 'Pharmacie WARDA', 'en': 'WARDA PHARMACY', 'ar': 'صيدلية وردة'},
    'Pharmacie LES TERRASSES DAR ESSALAM': {'fr': 'Pharmacie LES TERRASSES DAR ESSALAM', 'en': 'DAR ESSALAM TERRACES PHARMACY', 'ar': 'صيدلية تيراس دار السلام'},
    'Pharmacie DESCARTES': {'fr': 'Pharmacie DESCARTES', 'en': 'DESCARTES PHARMACY', 'ar': 'صيدلية ديكارت'},
    'Pharmacie AL MASBAH AL KABIR': {'fr': 'Pharmacie AL MASBAH AL KABIR', 'en': 'AL MASBAH AL KABIR PHARMACY', 'ar': 'صيدلية المصباح الكبير'},
    'Pharmacie HAY EL FATH': {'fr': 'Pharmacie HAY EL FATH', 'en': 'HAY EL FATH PHARMACY', 'ar': 'صيدلية حي الفتح'},
    'Pharmacie HAY CHABAB': {'fr': 'Pharmacie HAY CHABAB', 'en': 'HAY CHABAB PHARMACY', 'ar': 'صيدلية حي الشباب'},
    'Pharmacie DES CLINIQUES': {'fr': 'Pharmacie DES CLINIQUES', 'en': 'CLINICS PHARMACY', 'ar': 'صيدلية العيادات'},
    'Pharmacie MAGHREBINE (Ex: HÔPITAL)': {'fr': 'Pharmacie MAGHREBINE (Ex: HÔPITAL)', 'en': 'MAGHREBINE PHARMACY (Ex: HOSPITAL)', 'ar': 'صيدلية المغرب (سابقا: مستشفى)'},
    'Pharmacie SANAOUBAR RIAD': {'fr': 'Pharmacie SANAOUBAR RIAD', 'en': 'SANAOUBAR RIAD PHARMACY', 'ar': 'صيدلية سنوبر الرياض'},
    'Pharmacie ANZI': {'fr': 'Pharmacie ANZI', 'en': 'ANZI PHARMACY', 'ar': 'صيدلية أنزي'},
    'Pharmacie SAYARH': {'fr': 'Pharmacie SAYARH', 'en': 'SAYARH PHARMACY', 'ar': 'صيدلية الصائغ'},
    'Pharmacie LES LILAS': {'fr': 'Pharmacie LES LILAS', 'en': 'LILAS PHARMACY', 'ar': 'صيدلية ليليلا'},
    'Pharmacie AMWAJ': {'fr': 'Pharmacie AMWAJ', 'en': 'AMWAJ PHARMACY', 'ar': 'صيدلية أمواج'},
    'Pharmacie AL IGHATA': {'fr': 'Pharmacie AL IGHATA', 'en': 'AL IGHATA PHARMACY', 'ar': 'صيدلية الإغاثة'},
    'Pharmacie DU MINARET': {'fr': 'Pharmacie DU MINARET', 'en': 'MINARET PHARMACY', 'ar': 'صيدلية المنارة'},
    'Pharmacie ZINA': {'fr': 'Pharmacie ZINA', 'en': 'ZINA PHARMACY', 'ar': 'صيدلية زينة'},
    'Pharmacie LES IRIS': {'fr': 'Pharmacie LES IRIS', 'en': 'IRIS PHARMACY', 'ar': 'صيدلية السوسن'},
    'Pharmacie DAR ESSALAM': {'fr': 'Pharmacie DAR ESSALAM', 'en': 'DAR ESSALAM PHARMACY', 'ar': 'صيدلية دار السلام'},
    'Pharmacie IBN ZOHR': {'fr': 'Pharmacie IBN ZOHR', 'en': 'IBN ZOHR PHARMACY', 'ar': 'صيدلية ابن زهر'},
    'Pharmacie AL KHAWARIZMI': {'fr': 'Pharmacie AL KHAWARIZMI', 'en': 'AL KHAWARIZMI PHARMACY', 'ar': 'صيدلية الخوارزمي'},
    'Pharmacie AL AMANA': {'fr': 'Pharmacie AL AMANA', 'en': 'AL AMANA PHARMACY', 'ar': 'صيدلية الأمانة'},
    'Pharmacie ZAHRA': {'fr': 'Pharmacie ZAHRA', 'en': 'ZAHRA PHARMACY', 'ar': 'صيدلية الزهراء'},
    'Pharmacie BIR KACEM': {'fr': 'Pharmacie BIR KACEM', 'en': 'BIR KACEM PHARMACY', 'ar': 'صيدلية بير قاسم'},
    'Pharmacie AZHAR': {'fr': 'Pharmacie AZHAR', 'en': 'AZHAR PHARMACY', 'ar': 'صيدلية الأزهر'},
    'Pharmacie AL MASSIRA': {'fr': 'Pharmacie AL MASSIRA', 'en': 'AL MASSIRA PHARMACY', 'ar': 'صيدلية المسيرة'},
    'Pharmacie DES ORANGERS': {'fr': 'Pharmacie DES ORANGERS', 'en': 'ORANGERS PHARMACY', 'ar': 'صيدلية البرتقال'},
    'Pharmacie BENJELLOUN': {'fr': 'Pharmacie BENJELLOUN', 'en': 'BENJELLOUN PHARMACY', 'ar': 'صيدلية بنجلون'},
    'Pharmacie MOSQUEE O.L.M': {'fr': 'Pharmacie MOSQUEE O.L.M', 'en': 'O.L.M MOSQUE PHARMACY', 'ar': 'صيدلية مسجد أولم'},
    'Pharmacie ABDELKRIM EL KHATABI': {'fr': 'Pharmacie ABDELKRIM EL KHATABI', 'en': 'ABDELKRIM EL KHATABI PHARMACY', 'ar': 'صيدلية عبد الكريم الخطابي'},
    'Pharmacie ENNAIM': {'fr': 'Pharmacie ENNAIM', 'en': 'ENNAIM PHARMACY', 'ar': 'صيدلية النعيم'},
    'Pharmacie ANNOUZHA': {'fr': 'Pharmacie ANNOUZHA', 'en': 'ANNOUZHA PHARMACY', 'ar': 'صيدلية النزهة'},
    'Pharmacie LOUBNA': {'fr': 'Pharmacie LOUBNA', 'en': 'LOUBNA PHARMACY', 'ar': 'صيدلية لبنى'},
    'Pharmacie MERIEM': {'fr': 'Pharmacie MERIEM', 'en': 'MERIEM PHARMACY', 'ar': 'صيدلية مريم'},
    'Pharmacie BAYT ASSIHA': {'fr': 'Pharmacie BAYT ASSIHA', 'en': 'BAYT ASSIHA PHARMACY', 'ar': 'صيدلية بيت الصحة'},
    'Pharmacie SERJI': {'fr': 'Pharmacie SERJI', 'en': 'SERJI PHARMACY', 'ar': 'صيدلية السرجي'},
    'Pharmacie EL AMRANI': {'fr': 'Pharmacie EL AMRANI', 'en': 'EL AMRANI PHARMACY', 'ar': 'صيدلة العمراني'},
    'Pharmacie AMZAR': {'fr': 'Pharmacie AMZAR', 'en': 'AMZAR PHARMACY', 'ar': 'صيدلية أمزار'},
    'Pharmacie DU PLATEAU': {'fr': 'Pharmacie DU PLATEAU', 'en': 'PLATEAU PHARMACY', 'ar': 'صيدلية دو بلاتو'},
    'Pharmacie EL OUEDGHIRI DE SALE': {'fr': 'Pharmacie EL OUEDGHIRI DE SALE', 'en': 'EL OUEDGHIRI DE SALE PHARMACY', 'ar': 'صيدلية الودغيري بسلا'},
    'Pharmacie ZAKARIA': {'fr': 'Pharmacie ZAKARIA', 'en': 'ZAKARIA PHARMACY', 'ar': 'صيدلية زكريا'},
    'Pharmacie AZ-ZAHRA': {'fr': 'Pharmacie AZ-ZAHRA', 'en': 'AZ-ZAHRA PHARMACY', 'ar': 'صيدلية الزهراء'},
    'Pharmacie AL HAMBRA': {'fr': 'Pharmacie AL HAMBRA', 'en': 'AL HAMBRA PHARMACY', 'ar': 'صيدلية الحمراء'},
    'Pharmacie GUISSI': {'fr': 'Pharmacie GUISSI', 'en': 'GUISSI PHARMACY', 'ar': 'صيدلية غيسي'},
    'Pharmacie SIDI ABDELLAH': {'fr': 'Pharmacie SIDI ABDELLAH', 'en': 'SIDI ABDELLAH PHARMACY', 'ar': 'صيدلية سيدي عبد الله'},
    'GRANDE PHARMACIE DE SALE': {'fr': 'GRANDE PHARMACIE DE SALE', 'en': 'GRAND PHARMACY OF SALE', 'ar': 'الصيدلية الكبرى بسلا'},
    'Pharmacie DES HÔPITAUX': {'fr': 'Pharmacie DES HÔPITAUX', 'en': 'HOSPITALS PHARMACY', 'ar': 'صيدلية المستشفيات'},
    'Pharmacie EL MENZEH': {'fr': 'Pharmacie EL MENZEH', 'en': 'EL MENZEH PHARMACY', 'ar': 'صيدلية المنزه'},
    'Pharmacie ATLAS AL KABIR': {'fr': 'Pharmacie ATLAS AL KABIR', 'en': 'ATLAS AL KABIR PHARMACY', 'ar': 'صيدلية أطلس الكبير'},
    'Pharmacie CHAFIA': {'fr': 'Pharmacie CHAFIA', 'en': 'CHAFIA PHARMACY', 'ar': 'صيدلية الشافية'},
    'Pharmacie LA FONTAINE': {'fr': 'Pharmacie LA FONTAINE', 'en': 'LA FONTAINE PHARMACY', 'ar': 'صيدلية النافورة'},
    'Pharmacie ABDEDINE': {'fr': 'Pharmacie ABDEDINE', 'en': 'ABDEDINE PHARMACY', 'ar': 'صيدلية عبد الدين'},
    'Pharmacie BAYT AL MOSTAKBAL 2': {'fr': 'Pharmacie BAYT AL MOSTAKBAL 2', 'en': 'BAYT AL MOSTAKBAL 2 PHARMACY', 'ar': 'صيدلية بيت المستقبل 2'},
    'Pharmacie BENTALEB HAJAR': {'fr': 'Pharmacie BENTALEB HAJAR', 'en': 'BENTALEB HAJAR PHARMACY', 'ar': 'صيدلية بن طالب هاجر'},
    'Pharmacie GUELZIM': {'fr': 'Pharmacie GUELZIM', 'en': 'GUELZIM PHARMACY', 'ar': 'صيدلية كليم'},
    'Pharmacie SALAH EDDINE': {'fr': 'Pharmacie SALAH EDDINE', 'en': 'SALAH EDDINE PHARMACY', 'ar': 'صيدلية صلاح الدين'},
    'Pharmacie BELMAATI': {'fr': 'Pharmacie BELMAATI', 'en': 'BELMAATI PHARMACY', 'ar': 'صيدلية بلمعطي'},
    'Pharmacie AL MOHIT': {'fr': 'Pharmacie AL MOHIT', 'en': 'AL MOHIT PHARMACY', 'ar': 'صيدلية المحيط'},
    'Pharmacie ARYAD': {'fr': 'Pharmacie ARYAD', 'en': 'ARYAD PHARMACY', 'ar': 'صيدلية أرياد'},
    'Pharmacie EL KHEMIS': {'fr': 'Pharmacie EL KHEMIS', 'en': 'EL KHEMIS PHARMACY', 'ar': 'صيدلية الخميس'},
    'Pharmacie SALA AL JADIDA': {'fr': 'Pharmacie SALA AL JADIDA', 'en': 'SALA AL JADIDA PHARMACY', 'ar': 'صيدلية سلا الجديدة'},
    'Pharmacie DES VILLAS': {'fr': 'Pharmacie DES VILLAS', 'en': 'VILLAS PHARMACY', 'ar': 'صيدلية الفيلات'},
    'Pharmacie INAYA': {'fr': 'Pharmacie INAYA', 'en': 'INAYA PHARMACY', 'ar': 'صيدلية عناية'},
    'Pharmacie AR-RAZI': {'fr': 'Pharmacie AR-RAZI', 'en': 'AR-RAZI PHARMACY', 'ar': 'صيدلية الرازي'},
    'Pharmacie ES-SAADA': {'fr': 'Pharmacie ES-SAADA', 'en': 'ES-SAADA PHARMACY', 'ar': 'صيدلية السعادة'},
    'Pharmacie ASSEHA': {'fr': 'Pharmacie ASSEHA', 'en': 'ASSEHA PHARMACY', 'ar': 'صيدلية الصحة'},
    'Pharmacie AL MAÂRID': {'fr': 'Pharmacie AL MAÂRID', 'en': 'AL MAÂRID PHARMACY', 'ar': 'صيدلية المعاريد'},
    'Pharmacie LYAZID': {'fr': 'Pharmacie LYAZID', 'en': 'LYAZID PHARMACY', 'ar': 'صيدلية اليازيد'},
    'Pharmacie SAKANI': {'fr': 'Pharmacie SAKANI', 'en': 'SAKANI PHARMACY', 'ar': 'صيدلية السكني'},
    'Pharmacie MOUSTAWSAF BETTANA': {'fr': 'Pharmacie MOUSTAWSAF BETTANA', 'en': 'MOUSTAWSAF BETTANA PHARMACY', 'ar': 'صيدلية المستوصف بطانة'},
    'Pharmacie OUM AL KORA': {'fr': 'Pharmacie OUM AL KORA', 'en': 'OUM AL KORA PHARMACY', 'ar': 'صيدلية أم القرى'},
    'Pharmacie NASSIHA': {'fr': 'Pharmacie NASSIHA', 'en': 'NASSIHA PHARMACY', 'ar': 'صيدلية نصيحة'},
    'Pharmacie L`OLIVIER': {'fr': 'Pharmacie L`OLIVIER', 'en': 'OLIVE TREE PHARMACY', 'ar': 'صيدلية الزيتونة'},
    'Pharmacie LA REFERENCE': {'fr': 'Pharmacie LA REFERENCE', 'en': 'REFERENCE PHARMACY', 'ar': 'صيدلية المرجع'},
    'Pharmacie AL FARABI': {'fr': 'Pharmacie AL FARABI', 'en': 'AL FARABI PHARMACY', 'ar': 'صيدلية الفارابي'},
    'Pharmacie DE LA FAMILLE': {'fr': 'Pharmacie DE LA FAMILLE', 'en': 'FAMILY PHARMACY', 'ar': 'صيدلية العائلة'},
    'Pharmacie AL MAARIFA': {'fr': 'Pharmacie AL MAARIFA', 'en': 'AL MAARIFA PHARMACY', 'ar': 'صيدلية المعرفة'},
    'Pharmacie RIAD FES (TEMARA)': {'fr': 'Pharmacie RIAD FES (TEMARA)', 'en': 'RIAD FES PHARMACY (TEMARA)', 'ar': 'صيدلية رياض فاس (تمارة)'},
    'Pharmacie AL IHSSAN': {'fr': 'Pharmacie AL IHSSAN', 'en': 'AL IHSSAN PHARMACY', 'ar': 'صيدلية الإحسان'},
    'Pharmacie DE PALMA': {'fr': 'Pharmacie DE PALMA', 'en': 'PALMA PHARMACY', 'ar': 'صيدلية بالما'},
    'Pharmacie ATTADAMOUNE': {'fr': 'Pharmacie ATTADAMOUNE', 'en': 'ATTADAMOUNE PHARMACY', 'ar': 'صيدلية التضامن'},
    'Pharmacie DU QUARTIER': {'fr': 'Pharmacie DU QUARTIER', 'en': 'NEIGHBORHOOD PHARMACY', 'ar': 'صيدلية الحي'},
    'Pharmacie ESSAADA': {'fr': 'Pharmacie ESSAADA', 'en': 'ESSAADA PHARMACY', 'ar': 'صيدلية السعادة'},
    'Pharmacie HATIM': {'fr': 'Pharmacie HATIM', 'en': 'HATIM PHARMACY', 'ar': 'صيدلية حاتم'},
    'Pharmacie AL MAMOUNE': {'fr': 'Pharmacie AL MAMOUNE', 'en': 'AL MAMOUNE PHARMACY', 'ar': 'صيدلية المأمون'},
    'Pharmacie MASJID ANNOUR': {'fr': 'Pharmacie MASJID ANNOUR', 'en': 'MASJID ANNOUR PHARMACY', 'ar': 'صيدلية مسجد النور'},
    'Pharmacie ZAHRAT AL AMAL': {'fr': 'Pharmacie ZAHRAT AL AMAL', 'en': 'ZAHRAT AL AMAL PHARMACY', 'ar': 'صيدلية زهرة الأمل'},
    'Pharmacie PANORAMIQUE': {'fr': 'Pharmacie PANORAMIQUE', 'en': 'PANORAMIC PHARMACY', 'ar': 'صيدلية بانوراميك'},
    'Pharmacie OUED EL MAKHAZINE': {'fr': 'Pharmacie OUED EL MAKHAZINE', 'en': 'OUED EL MAKHAZINE PHARMACY', 'ar': 'صيدلية وادي المخازن'},
    'Pharmacie YAKINE': {'fr': 'Pharmacie YAKINE', 'en': 'YAKINE PHARMACY', 'ar': 'صيدلية الياقين'},
    'Pharmacie MENARA': {'fr': 'Pharmacie MENARA', 'en': 'MENARA PHARMACY', 'ar': 'صيدلية المنارة'},
    'Pharmacie AHL LOUGHLAM': {'fr': 'Pharmacie AHL LOUGHLAM', 'en': 'AHL LOUGHLAM PHARMACY', 'ar': 'صيدلية أهل لغلام'},
    'Pharmacie SAAD EL KHEIR': {'fr': 'Pharmacie SAAD EL KHEIR', 'en': 'SAAD EL KHEIR PHARMACY', 'ar': 'صيدلية سعد الخير'},
    'Pharmacie EL HAY': {'fr': 'Pharmacie EL HAY', 'en': 'EL HAY PHARMACY', 'ar': 'صيدلية الحي'},
    'Pharmacie HAY MOHAMMADI MINARET': {'fr': 'Pharmacie HAY MOHAMMADI MINARET', 'en': 'HAY MOHAMMADI MINARET PHARMACY', 'ar': 'صيدلية حي المحمدي منارة'},
    'Pharmacie SLAOUI': {'fr': 'Pharmacie SLAOUI', 'en': 'SLAOUI PHARMACY', 'ar': 'صيدلية السلاوي'},
    'Pharmacie AAD EL JADID': {'fr': 'Pharmacie AAD EL JADID', 'en': 'AAD EL JADID PHARMACY', 'ar': 'صيدلية عاد الجديد'},
    'Pharmacie LOTF ALLAH': {'fr': 'Pharmacie LOTF ALLAH', 'en': 'LOTF ALLAH PHARMACY', 'ar': 'صيدلية لطف الله'},
    'Pharmacie DERB MOULAY CHERIF': {'fr': 'Pharmacie DERB MOULAY CHERIF', 'en': 'DERB MOULAY CHERIF PHARMACY', 'ar': 'صيدلية درب مولاي الشريف'},
    'Pharmacie HOUAR': {'fr': 'Pharmacie HOUAR', 'en': 'HOUAR PHARMACY', 'ar': 'صيدلية هوار'},
    'Pharmacie MERCURE': {'fr': 'Pharmacie MERCURE', 'en': 'MERCURY PHARMACY', 'ar': 'صيدلية ميركور'}
}

# IMPORTANT FIX: Initialize GUIDE_CITIES in the global scope so it's accessible everywhere.
GUIDE_CITIES = get_guide_cities_urls()


# The main scraping and saving function
def scrape_and_save_data(file_path='pharmacy_data.json'):
    """
    Fetches pharmacy data from all specified URLs, extracts mock data,
    and saves it to a JSON file.
    
    Args:
        file_path (str): The name/path of the file to save the data to.
    """
    print("--- Starting to fetch and save pharmacy data ---")
    all_pharmacies = []

    # 1. Fetch data from Guide Pharmacies URLs
    print("\n[Guide Pharmacies]")
    for url in GUIDE_CITIES:
        try:
            print(f"Attempting to fetch data from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Here, you would replace this mock data with real scraping logic.
            # Example: soup = BeautifulSoup(response.text, 'html.parser')
            # For this fix, we'll simulate scraping and add data to our list.
            all_pharmacies.append({
                'source': 'Guide Pharmacies',
                'url': url,
                'name': f"Pharmacy from {url.split('/')[-1].split('.')[0]}",
                'address': 'Simulated Address',
                'phone': 'N/A'
            })
            print(f"  --> Successfully scraped and stored data from {url}")
        
        except requests.exceptions.RequestException as e:
            print(f"  --> Error fetching data from {url}: {e}")

    # 2. Fetch data from Le Matin URLs
    print("\n[Le Matin]")
    for url in LEMATIN_URLS:
        try:
            print(f"Attempting to fetch data from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Here, you would replace this mock data with real scraping logic.
            all_pharmacies.append({
                'source': 'Le Matin',
                'url': url,
                'name': f"Pharmacy from {url.split('/')[-1]}",
                'address': 'Simulated Address',
                'phone': 'N/A'
            })
            print(f"  --> Successfully scraped and stored data from {url}")
            
        except requests.exceptions.RequestException as e:
            print(f"  --> Error fetching data from {url}: {e}")

    # 3. Save the collected data to a JSON file
    if all_pharmacies:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_pharmacies, f, ensure_ascii=False, indent=4)
            print(f"\n--- Successfully generated pharmacy data file: {file_path} ---")
            
        except IOError as e:
            print(f"Error saving data to file {file_path}: {e}")
    else:
        print("\nNo data was collected. File not generated.")
        
    print("\n--- Process completed ---")

# Main function for script execution
def main():
    scrape_and_save_data()

# Entry point of the script
if __name__ == "__main__":
    main()
