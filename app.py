from flask import Flask, render_template, request, session, jsonify
import json, random, csv, os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
import requests
from flask_mail import Mail, Message
from twilio.rest import Client
import pickle
import numpy as np

# ── Import all data + helpers ──────────────────────────────────────────────────
from crop_data import (
    STATES_DATA, STATES, CROP_CONDITIONS, STATE_CROPS, SEASONAL_RAINFALL,
    CROP_EMOJIS, CROP_HINDI_NAMES, CROP_DESCRIPTIONS, CROP_DESCRIPTIONS_HI,
    SEASON_CROPS, SOIL_CROPS, SOIL_VALUES,
    get_current_season, get_soil_values,
    get_state_valid_crops, get_season_valid_crops, get_soil_valid_crops,
    score_crop_against_weather, pick_best_from_rules, compute_irrigation_data,
    check_day_suitability, compute_analysis_status,
)

# ── Twilio ─────────────────────────────────────────────────────────────────────
account_sid   = os.environ.get("TWILIO_ACCOUNT_SID", "")
auth_token    = os.environ.get("TWILIO_AUTH_TOKEN", "")
twilio_number = os.environ.get("TWILIO_PHONE_NUMBER", "")
twilio_client = Client(account_sid, auth_token)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")

@app.context_processor
def inject_globals():
    return dict(
        request=request,
        session_name=session.get('name', ''),
        session_mobile=session.get('mobile', ''),
    )

# ── Mail ───────────────────────────────────────────────────────────────────────
app.config.update(
    MAIL_SERVER='smtp.gmail.com', MAIL_PORT=587, MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME', ''),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD', '')
)
mail = Mail(app)

# ── ML Model ───────────────────────────────────────────────────────────────────
model = pickle.load(open("model.pkl", "rb"))


# ════════════════════════════════════════════════════════════════════════════════
#  CSV DATABASE
# ════════════════════════════════════════════════════════════════════════════════

CSV_FILE = "users.csv"
CSV_FIELDS = ["phone", "name", "password", "state", "district"]

# ── User history folder ────────────────────────────────────────────────────────
USER_DETAILS_DIR = "user details"

HIST_REC_FIELDS = [
    "datetime", "activity_type",
    "crop", "crop_hindi", "confidence",
    "soil", "season", "state", "district",
    "temperature_c", "humidity_pct", "rainfall_mm",
    "irrigation_needed_mm", "irrigation_label",
    "alternatives", "reason"
]
HIST_ANA_FIELDS = [
    "datetime", "activity_type",
    "crop", "district",
    "total_days", "good_days", "bad_days",
    "overall_status", "day_results"
]


def _ensure_user_details_dir():
    os.makedirs(USER_DETAILS_DIR, exist_ok=True)


def _user_csv_path(phone):
    return os.path.join(USER_DETAILS_DIR, f"{phone}.csv")


def save_recommendation_history(phone, row: dict):
    """Append a crop-recommendation record to the user's history file."""
    _ensure_user_details_dir()
    path   = _user_csv_path(phone)
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HIST_REC_FIELDS + HIST_ANA_FIELDS,
                           extrasaction="ignore")
        if not exists:
            w.writeheader()
        w.writerow(row)


def save_analysis_history(phone, row: dict):
    """Append a crop-analysis record to the user's history file."""
    _ensure_user_details_dir()
    path   = _user_csv_path(phone)
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        # unified fieldset so both types live in the same file
        all_fields = list(dict.fromkeys(HIST_REC_FIELDS + HIST_ANA_FIELDS))
        w = csv.DictWriter(f, fieldnames=all_fields, extrasaction="ignore")
        if not exists:
            w.writeheader()
        w.writerow(row)


def load_user_history(phone):
    """Return list of history dicts for the user, newest-first."""
    path = _user_csv_path(phone)
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return list(reversed(rows))


_ensure_user_details_dir()


def hash_password(password):
    return password


def init_csv():
    """Create users.csv if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
        print("users.csv created.")


def csv_get_user(phone):
    """Return user row dict by phone number, or None."""
    if not os.path.exists(CSV_FILE):
        return None
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["phone"] == phone:
                return row
    return None


def csv_user_exists(phone):
    """Check if a user with this phone number exists."""
    return csv_get_user(phone) is not None


def csv_create_user(phone, name, password, state, district):
    """Add a new user to the CSV. Returns True on success, False if phone exists."""
    if csv_user_exists(phone):
        return False
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow({
            "phone":    phone,
            "name":     name,
            "password": hash_password(password),
            "state":    state,
            "district": district,
        })
    return True


def csv_verify_login(phone, password):
    """Verify phone + password. Returns user row on success, None on failure."""
    user = csv_get_user(phone)
    if user and user["password"] == hash_password(password):
        return user
    return None


init_csv()


# ════════════════════════════════════════════════════════════════════════════════
#  WEATHER
# ════════════════════════════════════════════════════════════════════════════════

def get_weather(district):
    api_key = os.environ.get("OPENWEATHER_API_KEY", "")
    try:
        res = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={district},IN&appid={api_key}&units=metric", timeout=5
        ).json()
        return f"{res['main']['temp']}°C, {res['weather'][0]['description']}"
    except:
        return "Not available"


def get_weather_details(district, state, season):
    api_key = os.environ.get("OPENWEATHER_API_KEY", "")
    avg_rain = SEASONAL_RAINFALL.get(state, {}).get(season, 80.0)
    try:
        res      = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={district},IN&appid={api_key}&units=metric", timeout=5
        ).json()
        temp     = float(res['main']['temp'])
        humidity = float(res['main']['humidity'])
        live_r   = res.get('rain', {}).get('1h', 0) or 0
        return temp, humidity, float(live_r) if live_r > 0 else avg_rain
    except:
        return 25.0, 70.0, avg_rain


# ════════════════════════════════════════════════════════════════════════════════
#  HYBRID PREDICTION ENGINE
# ════════════════════════════════════════════════════════════════════════════════

def run_smart_prediction(soil, district, state, season):
    temp, humidity, rainfall = get_weather_details(district, state, season)
    N, P, K, ph = get_soil_values(soil)
    ml_crop = str(model.predict(
        np.array([[N, P, K, temp, humidity, ph, rainfall]], dtype=float)
    )[0]).lower()

    state_crops  = set(get_state_valid_crops(state))
    season_crops = set(get_season_valid_crops(season))
    soil_crops   = set(get_soil_valid_crops(soil))
    all_valid    = state_crops & season_crops & soil_crops
    state_soil   = state_crops & soil_crops
    state_season = state_crops & season_crops

    if ml_crop in all_valid:
        confidence = "HIGH"; final_crop = ml_crop
        reason    = (f"ML model and regional data agree: {ml_crop.capitalize()} suits "
                     f"{state}'s {soil} soil in {season} season.")
        reason_hi = (f"ML मॉडल और क्षेत्रीय डेटा सहमत: "
                     f"{CROP_HINDI_NAMES.get(ml_crop, ml_crop.capitalize())} "
                     f"{state} की {soil} मिट्टी में {season} मौसम के लिए उपयुक्त।")
    elif ml_crop in state_soil:
        confidence = "MEDIUM"; final_crop = ml_crop
        reason    = f"{ml_crop.capitalize()} grows in {state} and suits {soil} soil year-round."
        reason_hi = (f"{CROP_HINDI_NAMES.get(ml_crop, ml_crop.capitalize())} "
                     f"{state} में उगाई जाती है और {soil} मिट्टी के लिए उपयुक्त है।")
    elif ml_crop in state_season:
        confidence = "LOW"; final_crop = ml_crop
        reason    = (f"{ml_crop.capitalize()} grows in {state} in {season} but "
                     f"may not perfectly suit {soil} soil.")
        reason_hi = (f"{CROP_HINDI_NAMES.get(ml_crop, ml_crop.capitalize())} "
                     f"{state} में {season} में उगती है लेकिन "
                     f"{soil} मिट्टी के लिए पूरी तरह उचित नहीं।")
    else:
        confidence = "LOW"
        pool = all_valid or state_soil or state_season or state_crops
        final_crop = (pick_best_from_rules(pool, temp, humidity, rainfall)
                      if pool else ml_crop)
        reason    = (f"ML suggested '{ml_crop}' but it is not grown in {state}. "
                     f"Recommending {final_crop.capitalize()} based on regional data.")
        reason_hi = (f"ML ने '{ml_crop}' सुझाया लेकिन यह {state} में नहीं उगती। "
                     f"{CROP_HINDI_NAMES.get(final_crop, final_crop.capitalize())} "
                     f"क्षेत्रीय डेटा के आधार पर सिफारिश की गई है।")

    alt_pool     = (all_valid if all_valid else state_crops) - {final_crop}
    alternatives = sorted(alt_pool,
        key=lambda c: score_crop_against_weather(c, temp, humidity, rainfall))[:2]
    return final_crop, confidence, reason, reason_hi, alternatives, temp, humidity, rainfall


# ════════════════════════════════════════════════════════════════════════════════
#  OTP + SMS HELPERS  (OTP used only for signup)
# ════════════════════════════════════════════════════════════════════════════════

def generate_otp():
    otp=str(random.randint(100000, 999999))
    print(otp)
    return otp


def send_sms(mobile, body):
    twilio_client.messages.create(body=body, from_=twilio_number, to="+91" + mobile)


def send_crop_recommendation_sms(mobile, crop, crop_hi, district, season, confidence, lang):
    if lang == 'hi':
        msg = (f"Kisan Suvidha - Fasal Sifarish\n"
               f"Fasal: {crop_hi or crop.capitalize()}\n"
               f"Zila: {district} | Mausam: {season}\n"
               f"Vishwas: {confidence}\n"
               f"App kholein poori jaankari ke liye.")
    else:
        msg = (f"Kisan Suvidha - Crop Recommendation\n"
               f"Crop: {crop.capitalize()}\n"
               f"District: {district} | Season: {season}\n"
               f"Confidence: {confidence}\n"
               f"Open the app for full details.")
    try:
        send_sms(mobile, msg)
    except Exception as e:
        print("Crop SMS failed:", e)


# ════════════════════════════════════════════════════════════════════════════════
#  HINDI TRANSLATION DATA (passed to login.html)
# ════════════════════════════════════════════════════════════════════════════════

STATES_HINDI = {
    "Andhra Pradesh":"आंध्र प्रदेश","Arunachal Pradesh":"अरुणाचल प्रदेश",
    "Assam":"असम","Bihar":"बिहार","Chhattisgarh":"छत्तीसगढ़","Goa":"गोआ",
    "Gujarat":"गुजरात","Haryana":"हरियाणा","Himachal Pradesh":"हिमाचल प्रदेश",
    "Jharkhand":"झारखंड","Karnataka":"कर्नाटक","Kerala":"केरल",
    "Madhya Pradesh":"मध्य प्रदेश","Maharashtra":"महाराष्ट्र","Manipur":"मणिपुर",
    "Meghalaya":"मेघालय","Mizoram":"मिज़ोरम","Nagaland":"नागालैंड","Odisha":"ओडिशा",
    "Punjab":"पंजाब","Rajasthan":"राजस्थान","Sikkim":"सिक्किम",
    "Tamil Nadu":"तमिल नाडु","Telangana":"तेलंगाना","Tripura":"त्रिपुरा",
    "Uttar Pradesh":"उत्तर प्रदेश","Uttarakhand":"उत्तराखंड","West Bengal":"पश्चिम बंगाल",
}

DISTRICTS_HINDI = {
    "Anantapur":"अनंतपुर","Chittoor":"चित्तूर","Guntur":"गुंटूर","Krishna":"कृष्णा",
    "Kurnool":"कुर्नूल","Nellore":"नेल्लोर","Prakasam":"प्रकाशम","Srikakulam":"श्रीकाकुलम",
    "Visakhapatnam":"विशाखापट्टनम","Vizianagaram":"विजयनगरम",
    "West Godavari":"पश्चिम गोदावरी","East Godavari":"पूर्वी गोदावरी",
    "Baksa":"बक्सा","Barpeta":"बारपेटा","Bongaigaon":"बोंगाईगांव","Cachar":"कछार",
    "Darrang":"दरांग","Dhemaji":"धेमाजी","Dhubri":"धुबरी","Dibrugarh":"डिब्रूगढ़",
    "Goalpara":"गोआलपाड़ा","Golaghat":"गोलाघाट","Hailakandi":"हैलाकांडी",
    "Jorhat":"जोरहाट","Kamrup":"कामरूप","Karbi Anglong":"कार्बी आंगलोंग",
    "Karimganj":"करीमगंज","Kokrajhar":"कोकराझार","Lakhimpur":"लखीमपुर",
    "Morigaon":"मोरीगांव","Nagaon":"नगांव","Nalbari":"नलबाड़ी","Sivasagar":"शिवसागर",
    "Sonitpur":"सोनितपुर","Tinsukia":"तिनसुकिया",
    "Araria":"अरारिया","Aurangabad":"औरंगाबाद","Banka":"बांका","Begusarai":"बेगूसराय",
    "Bhagalpur":"भागलपुर","Bhojpur":"भोजपुर","Buxar":"बक्सर","Darbhanga":"दरभंगा",
    "Gaya":"गया","Gopalganj":"गोपालगंज","Jamui":"जमुई","Jehanabad":"जहानाबाद",
    "Katihar":"कटिहार","Khagaria":"खगड़िया","Kishanganj":"किशनगंज","Lakhisarai":"लखीसराय",
    "Madhubani":"मधुबनी","Munger":"मुंगेर","Muzaffarpur":"मुजफ्फरपुर","Nalanda":"नालंदा",
    "Nawada":"नवादा","Patna":"पटना","Purnia":"पूर्णिया","Rohtas":"रोहतास",
    "Saharsa":"सहरसा","Samastipur":"समस्तीपुर","Saran":"सारण","Siwan":"सीवान","Vaishali":"वैशाली",
    "Raipur":"रायपुर","Durg":"दुर्ग","Bilaspur":"बिलासपुर","Korba":"कोरबा",
    "Raigarh":"रायगढ़","Rajnandgaon":"राजनांदगांव","Janjgir-Champa":"जांजगीर-चांपा",
    "Mahasamund":"महासमुंद","Kanker":"कांकेर","Bastar":"बस्तर",
    "Dantewada":"दंतेवाड़ा","Surguja":"सरगुजा",
    "North Goa":"उत्तर गोआ","South Goa":"दक्षिण गोआ",
    "Ahmedabad":"अहमदाबाद","Surat":"सूरत","Vadodara":"वडोदरा","Rajkot":"राजकोट",
    "Bhavnagar":"भावनगर","Jamnagar":"जामनगर","Junagadh":"जूनागढ़","Kutch":"कच्छ",
    "Gandhinagar":"गांधीनगर","Anand":"आनंद","Bharuch":"भरूच","Navsari":"नवसारी",
    "Ambala":"अंबाला","Bhiwani":"भिवानी","Faridabad":"फरीदाबाद","Fatehabad":"फतेहाबाद",
    "Gurgaon":"गुरुग्राम","Hisar":"हिसार","Jhajjar":"झज्जर","Jind":"जींद","Kaithal":"कैथल",
    "Karnal":"करनाल","Kurukshetra":"कुरुक्षेत्र","Panipat":"पानीपत","Rewari":"रेवाड़ी",
    "Rohtak":"रोहतक","Sirsa":"सिरसा","Sonipat":"सोनीपत","Yamunanagar":"यमुनानगर",
    "Chamba":"चंबा","Hamirpur":"हमीरपुर","Kangra":"कांगड़ा","Kinnaur":"किन्नौर",
    "Kullu":"कुल्लू","Mandi":"मंडी","Shimla":"शिमला","Sirmaur":"सिरमौर","Solan":"सोलन","Una":"ऊना",
    "Bokaro":"बोकारो","Chatra":"चतरा","Deoghar":"देवघर","Dhanbad":"धनबाद","Dumka":"दुमका",
    "East Singhbhum":"पूर्वी सिंहभूम","Garhwa":"गढ़वा","Giridih":"गिरिडीह","Godda":"गोड्डा",
    "Gumla":"गुमला","Hazaribagh":"हज़ारीबाग","Jamtara":"जामताड़ा","Khunti":"खूंटी",
    "Koderma":"कोडरमा","Latehar":"लातेहार","Lohardaga":"लोहरदगा","Pakur":"पाकुड़",
    "Palamu":"पलामू","Ramgarh":"रामगढ़","Ranchi":"रांची","Sahebganj":"साहेबगंज",
    "Bagalkot":"बागलकोट","Ballari":"बल्लारी","Belagavi":"बेलगावी",
    "Bengaluru Rural":"बेंगलुरु ग्रामीण","Bengaluru Urban":"बेंगलुरु शहरी",
    "Bidar":"बीदर","Chamarajanagar":"चामराजनगर","Chikkaballapur":"चिक्काबल्लापुर",
    "Chikkamagaluru":"चिक्कमगलुरू","Chitradurga":"चित्रदुर्ग","Dakshina Kannada":"दक्षिण कन्नड़",
    "Davanagere":"दावणगेरे","Dharwad":"धारवाड़","Gadag":"गदग","Hassan":"हासन",
    "Haveri":"हावेरी","Kalaburagi":"कलबुर्गी","Kodagu":"कोडगु","Kolar":"कोलार",
    "Koppal":"कोप्पल","Mandya":"मांड्या","Mysuru":"मैसूरू","Raichur":"रायचूर",
    "Shivamogga":"शिवमोग्गा","Tumakuru":"तुमकुरू","Udupi":"उडुपी",
    "Uttara Kannada":"उत्तर कन्नड़","Vijayapura":"विजयपुरा","Yadgir":"यादगीर",
    "Alappuzha":"अलप्पुझा","Ernakulam":"एर्नाकुलम","Idukki":"इडुक्की","Kannur":"कन्नूर",
    "Kasaragod":"कासरगोड","Kollam":"कोल्लम","Kottayam":"कोट्टायम","Kozhikode":"कोझिकोड",
    "Malappuram":"मलप्पुरम","Palakkad":"पलक्कड़","Pathanamthitta":"पत्तनमतिट्टा",
    "Thiruvananthapuram":"तिरुवनंतपुरम","Thrissur":"त्रिशूर","Wayanad":"वायनाड",
    "Agar Malwa":"आगर मालवा","Alirajpur":"अलीराजपुर","Anuppur":"अनूपपुर",
    "Ashoknagar":"अशोकनगर","Balaghat":"बालाघाट","Barwani":"बड़वानी","Betul":"बैतूल",
    "Bhind":"भिंड","Bhopal":"भोपाल","Burhanpur":"बुरहानपुर","Chhatarpur":"छतरपुर",
    "Chhindwara":"छिंदवाड़ा","Damoh":"दमोह","Datia":"दतिया","Dewas":"देवास","Dhar":"धार",
    "Dindori":"डिंडोरी","Guna":"गुना","Gwalior":"ग्वालियर","Harda":"हरदा","Indore":"इंदौर",
    "Jabalpur":"जबलपुर","Jhabua":"झाबुआ","Katni":"कटनी","Khandwa":"खंडवा",
    "Khargone":"खरगोन","Mandla":"मंडला","Mandsaur":"मंदसौर","Morena":"मुरैना",
    "Narsinghpur":"नरसिंहपुर","Neemuch":"नीमच","Panna":"पन्ना","Raisen":"रायसेन",
    "Rajgarh":"राजगढ़","Ratlam":"रतलाम","Rewa":"रीवा","Sagar":"सागर","Satna":"सतना",
    "Sehore":"सीहोर","Seoni":"सिवनी","Shahdol":"शहडोल","Shajapur":"शाजापुर",
    "Sheopur":"श्योपुर","Shivpuri":"शिवपुरी","Sidhi":"सीधी","Singrauli":"सिंगरौली",
    "Tikamgarh":"टीकमगढ़","Ujjain":"उज्जैन","Umaria":"उमरिया","Vidisha":"विदिशा",
    "Mumbai":"मुंबई","Mumbai Suburban":"मुंबई उपनगरीय","Pune":"पुणे","Nagpur":"नागपुर",
    "Nashik":"नाशिक","Thane":"ठाणे","Palghar":"पालघर","Kolhapur":"कोल्हापुर",
    "Solapur":"सोलापुर","Satara":"सातारा","Amravati":"अमरावती","Akola":"अकोला",
    "Yavatmal":"यवतमाल","Wardha":"वर्धा","Chandrapur":"चंद्रपुर","Gondia":"गोंदिया",
    "Ratnagiri":"रत्नागिरी","Sindhudurg":"सिंधुदुर्ग","Jalgaon":"जलगांव","Dhule":"धुले",
    "Nanded":"नांदेड","Latur":"लातूर","Beed":"बीड","Osmanabad":"उस्मानाबाद",
    "Parbhani":"परभणी","Hingoli":"हिंगोली","Bhandara":"भंडारा","Gadchiroli":"गडचिरोली",
    "Angul":"अंगुल","Balangir":"बलांगीर","Balasore":"बालासोर","Bargarh":"बरगढ़",
    "Bhadrak":"भद्रक","Cuttack":"कटक","Deogarh":"देवगढ़","Dhenkanal":"ढेंकानाल",
    "Ganjam":"गंजाम","Gajapati":"गजपति","Jharsuguda":"झारसुगुड़ा","Kalahandi":"कालाहांडी",
    "Kendrapara":"केंद्रपाड़ा","Keonjhar":"क्योंझर","Khordha":"खोर्धा","Koraput":"कोरापुट",
    "Mayurbhanj":"मयूरभंज","Nabarangpur":"नबरंगपुर","Nayagarh":"नयागढ़","Puri":"पुरी",
    "Rayagada":"रायगडा","Sambalpur":"संबलपुर","Sundargarh":"सुंदरगढ़",
    "Amritsar":"अमृतसर","Bathinda":"बठिंडा","Firozpur":"फिरोजपुर","Gurdaspur":"गुरदासपुर",
    "Hoshiarpur":"होशियारपुर","Jalandhar":"जालंधर","Kapurthala":"कपूरथला","Ludhiana":"लुधियाना",
    "Mansa":"मानसा","Moga":"मोगा","Patiala":"पटियाला","Rupnagar":"रूपनगर","Sangrur":"संगरूर",
    "Ajmer":"अजमेर","Alwar":"अलवर","Banswara":"बांसवाड़ा","Baran":"बारां","Barmer":"बाड़मेर",
    "Bharatpur":"भरतपुर","Bhilwara":"भीलवाड़ा","Bikaner":"बीकानेर","Chittorgarh":"चित्तौड़गढ़",
    "Churu":"चूरू","Dausa":"दौसा","Dholpur":"धौलपुर","Dungarpur":"डूंगरपुर",
    "Hanumangarh":"हनुमानगढ़","Jaipur":"जयपुर","Jaisalmer":"जैसलमेर","Jalore":"जालोर",
    "Jhalawar":"झालावाड़","Jhunjhunu":"झुंझुनू","Jodhpur":"जोधपुर","Karauli":"करौली",
    "Kota":"कोटा","Nagaur":"नागौर","Pali":"पाली","Sikar":"सीकर","Sirohi":"सिरोही",
    "Sri Ganganagar":"श्री गंगानगर","Tonk":"टोंक","Udaipur":"उदयपुर",
    "Chennai":"चेन्नई","Coimbatore":"कोयंबटूर","Madurai":"मदुरई","Salem":"सेलम",
    "Tiruchirappalli":"तिरुचिरापल्ली","Tirunelveli":"तिरुनेलवेली","Vellore":"वेल्लोर",
    "Erode":"इरोड","Thoothukudi":"तूतुकुड़ी","Dindigul":"डिंडीगुल","Thanjavur":"तंजावुर",
    "Hyderabad":"हैदराबाद","Warangal":"वारंगल","Nizamabad":"निजामाबाद",
    "Karimnagar":"करीमनगर","Khammam":"खम्मम","Mahbubnagar":"महबूबनगर","Adilabad":"आदिलाबाद",
    "Agra":"आगरा","Aligarh":"अलीगढ़","Prayagraj":"प्रयागराज","Amethi":"अमेठी",
    "Amroha":"अमरोहा","Auraiya":"औरैया","Ayodhya":"अयोध्या","Azamgarh":"आज़मगढ़",
    "Baghpat":"बागपत","Bahraich":"बहराइच","Ballia":"बलिया","Balrampur":"बलरामपुर",
    "Banda":"बांदा","Barabanki":"बाराबंकी","Bareilly":"बरेली","Basti":"बस्ती",
    "Bijnor":"बिजनौर","Bulandshahr":"बुलंदशहर","Chandauli":"चंदौली","Deoria":"देवरिया",
    "Etawah":"इटावा","Farrukhabad":"फर्रुखाबाद","Fatehpur":"फतेहपुर","Firozabad":"फिरोजाबाद",
    "Ghaziabad":"गाजियाबाद","Ghazipur":"ग़ाज़ीपुर","Gonda":"गोंडा","Gorakhpur":"गोरखपुर",
    "Jaunpur":"जौनपुर","Jhansi":"झाँसी","Kanpur Nagar":"कानपुर नगर","Lucknow":"लखनऊ",
    "Mathura":"मथुरा","Meerut":"मेरठ","Mirzapur":"मिर्जापुर","Moradabad":"मुरादाबाद",
    "Pratapgarh":"प्रतापगढ़","Raebareli":"रायबरेली","Saharanpur":"सहारनपुर",
    "Sitapur":"सीतापुर","Varanasi":"वाराणसी",
    "Dehradun":"देहरादून","Haridwar":"हरिद्वार","Nainital":"नैनीताल",
    "Pauri Garhwal":"पौड़ी गढ़वाल","Tehri Garhwal":"टिहरी गढ़वाल",
    "Udham Singh Nagar":"उधम सिंह नगर","Almora":"अल्मोड़ा","Chamoli":"चमोली",
    "Champawat":"चंपावत","Pithoragarh":"पिथौरागढ़","Rudraprayag":"रुद्रप्रयाग","Bageshwar":"बागेश्वर",
    "Kolkata":"कोलकाता","Howrah":"हावड़ा","Darjeeling":"दार्जिलिंग","Jalpaiguri":"जलपाईगुड़ी",
    "Cooch Behar":"कूचबिहार","Malda":"मालदा","Murshidabad":"मुर्शिदाबाद","Nadia":"नदिया",
    "Hooghly":"हुगली","North 24 Parganas":"उत्तर 24 परगना","South 24 Parganas":"दक्षिण 24 परगना",
    "Bankura":"बांकुड़ा","Purulia":"पुरुलिया","Paschim Medinipur":"पश्चिम मेदिनीपुर",
    "Purba Medinipur":"पूर्व मेदिनीपुर",
}


def _login_render(lang, active_tab='signin', error=None, message=None,
                  selected_state='', districts=None):
    """Render login.html with all required context."""
    return render_template(
        "login.html", lang=lang,
        states=STATES,
        states_json=json.dumps(STATES_DATA),
        states_hindi_json=json.dumps(STATES_HINDI),
        districts_hindi_json=json.dumps(DISTRICTS_HINDI),
        statesHindi=STATES_HINDI,
        districtsHindi=DISTRICTS_HINDI,
        districts=districts or [],
        selected_state=selected_state,
        active_tab=active_tab,
        error=error, message=message,
    )


# ════════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ════════════════════════════════════════════════════════════════════════════════

@app.route('/set_lang')
def set_lang():
    from flask import redirect, url_for
    lang = request.args.get('lang', 'en')
    session['lang'] = lang
    back = request.referrer or url_for('choose')
    from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
    parsed = urlparse(back)
    params = parse_qs(parsed.query)
    params['lang'] = [lang]
    new_query = urlencode({k: v[0] for k, v in params.items()})
    new_url = urlunparse(parsed._replace(query=new_query))
    return redirect(new_url)


@app.route('/')
def home():
    return render_template('language.html')


# ── Send OTP (used only for signup / new user registration) ───────────────────
@app.route('/send_otp', methods=['POST'])
def send_otp():
    data   = request.get_json()
    mobile = data.get('mobile', '').strip()
    lang   = session.get('lang', 'en')

    if not mobile.isdigit() or len(mobile) != 10:
        err = "अमान्य मोबाइल नंबर।" if lang == 'hi' else "Invalid mobile number."
        return jsonify(success=False, error=err)

    # Check if user already exists — if so, they should login not register
    if csv_user_exists(mobile):
        err = ("यह नंबर पहले से पंजीकृत है। कृपया साइन इन करें।"
               if lang == 'hi'
               else "This number is already registered. Please sign in instead.")
        return jsonify(success=False, error=err, already_registered=True)

    otp = generate_otp()
    print(f"OTP [{mobile}]: {otp}")   # dev only
    session.update({
        'otp': otp,
        'otp_mobile': mobile,
        'otp_expiry': (datetime.now() + timedelta(minutes=5)).isoformat()
    })
    try:
        sms_body = (f"Aapka Kisan Suvidha OTP hai: {otp}. 5 minute mein valid."
                    if lang == 'hi'
                    else f"Your Kisan Suvidha OTP is: {otp}. Valid for 5 minutes.")
        send_sms(mobile, sms_body)
        return jsonify(success=True)
    except Exception as e:
        print("OTP SMS failed:", e)
        return jsonify(success=False, error=str(e))


# ── Sign In (phone + password, no OTP) ────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = request.args.get('lang') or request.form.get('lang') or session.get('lang', 'en')
    session['lang'] = lang

    if request.method == 'GET':
        return _login_render(lang, active_tab='signin')

    mobile   = request.form.get('mobile', '').strip()
    password = request.form.get('password', '').strip()

    # Validate phone number format
    if not mobile.isdigit() or len(mobile) != 10:
        err = ("सही 10 अंकों का मोबाइल नंबर दर्ज करें।"
               if lang == 'hi' else "Enter a valid 10-digit mobile number.")
        return _login_render(lang, 'signin', error=err)

    # Check if user exists in CSV
    if not csv_user_exists(mobile):
        err = ("यह नंबर पंजीकृत नहीं है। कृपया पहले साइन अप करें।"
               if lang == 'hi'
               else "This number is not registered. Please sign up first.")
        return _login_render(lang, 'signin', error=err)

    # Verify password
    user = csv_verify_login(mobile, password)
    if not user:
        err = ("गलत पासवर्ड। पुनः प्रयास करें।"
               if lang == 'hi' else "Incorrect password. Please try again.")
        return _login_render(lang, 'signin', error=err)

    # Login successful
    session.update({
        'mobile':   mobile,
        'name':     user['name'],
        'state':    user['state'],
        'district': user['district'],
        'lang':     lang,
    })

    district = user['district']
    if district:
        return render_template("choose.html", lang=lang, district=district)

    return _login_render(lang, 'signin',
        message=("साइन इन सफल! अपना जिला चुनें।" if lang == 'hi'
                 else "Signed in! Please select your district."),
        selected_state=user['state'],
        districts=STATES_DATA.get(user['state'], []))


# ── Sign Up (phone + name + password + OTP verification) ──────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    lang = request.args.get('lang') or request.form.get('lang') or session.get('lang', 'en')
    session['lang'] = lang

    if request.method == 'GET':
        return _login_render(lang, active_tab='signup')

    name = request.form.get('name', '').strip()
    mobile = request.form.get('mobile', '').strip()
    password  = request.form.get('password', '').strip()
    otp_entered  = request.form.get('otp', '').strip()
    selected_state    = request.form.get('state', '').strip()
    selected_district = request.form.get('district', '').strip()

    # Basic field validation
    if not name:
        return _login_render(lang, 'signup',
            error="नाम आवश्यक है।" if lang == 'hi' else "Name is required.")
    if not mobile.isdigit() or len(mobile) != 10:
        return _login_render(lang, 'signup',
            error=("सही 10 अंकों का मोबाइल नंबर दर्ज करें।" if lang == 'hi'
                   else "Enter a valid 10-digit mobile number."))
    if not password or len(password) < 6:
        return _login_render(lang, 'signup',
            error=("पासवर्ड कम से कम 6 अक्षर का होना चाहिए।" if lang == 'hi'
                   else "Password must be at least 6 characters."))

    # Check if phone already registered
    if csv_user_exists(mobile):
        return _login_render(lang, 'signup',
            error=("यह नंबर पहले से पंजीकृत है। साइन इन करें।" if lang == 'hi'
                   else "This number is already registered. Please sign in."))

    # OTP validation
    stored_otp    = session.get('otp')
    stored_mobile = session.get('otp_mobile')
    expiry_str    = session.get('otp_expiry')
    error = None
    if not stored_otp:
        error = "पहले OTP मंगाएं।" if lang == 'hi' else "Please request an OTP first."
    elif mobile != stored_mobile:
        error = ("मोबाइल नंबर OTP से मेल नहीं खाता।" if lang == 'hi'
                 else "Mobile number does not match OTP.")
    elif datetime.now() > datetime.fromisoformat(expiry_str):
        error = ("OTP समाप्त हो गया।" if lang == 'hi'
                 else "OTP expired. Request a new one.")
    elif otp_entered != stored_otp:
        error = "गलत OTP।" if lang == 'hi' else "Incorrect OTP."

    if error:
        return _login_render(lang, 'signup', error=error,
                             selected_state=selected_state,
                             districts=STATES_DATA.get(selected_state, []))

    session.pop('otp', None); session.pop('otp_mobile', None); session.pop('otp_expiry', None)

    # Save to CSV
    csv_create_user(mobile, name, password, selected_state, selected_district)

    session.update({
        'mobile':   mobile,
        'name':     name,
        'state':    selected_state,
        'district': selected_district,
        'lang':     lang,
    })

    # Welcome SMS
    try:
        send_sms(mobile,
                 f"Namaste {name}! Kisan Suvidha mein aapka swagat hai."
                 if lang == 'hi'
                 else f"Hello {name}! Welcome to Kisan Suvidha. Happy farming!")
    except Exception as e:
        print("Welcome SMS failed:", e)

    if selected_district:
        return render_template("choose.html", lang=lang, district=selected_district)

    return _login_render(lang, 'signin',
        message=("खाता बन गया! अब साइन इन करें।" if lang == 'hi'
                 else "Account created! Please sign in."),
        selected_state=selected_state,
        districts=STATES_DATA.get(selected_state, []))


# ── Other pages ────────────────────────────────────────────────────────────────
@app.route('/choose')
def choose():
    lang = request.args.get('lang') or session.get('lang', 'en')
    session['lang'] = lang
    return render_template('choose.html', lang=lang, district=session.get('district', 'Unknown'))


@app.route('/crop_page')
def crop_page():
    lang = request.args.get('lang') or session.get('lang', 'en')
    session['lang'] = lang
    district = session.get('district', 'Unknown')
    return render_template('crop.html', lang=lang, auto_season=get_current_season(),
                           district=district, weather=get_weather(district))


@app.route('/analysis_page')
def analysis_page():
    lang = request.args.get('lang') or session.get('lang', 'en')
    session['lang'] = lang
    return render_template('analysis.html', lang=lang,
                           district=session.get('district', 'Unknown'),
                           crop_rules_json=json.dumps(CROP_CONDITIONS))


# ── Crop recommendation ────────────────────────────────────────────────────────
@app.route('/crop', methods=['POST'])
def crop():
    lang     = session.get('lang', 'en')
    soil     = request.form.get('soil', '').strip()
    season   = request.form.get('season', get_current_season())
    district = session.get('district', 'Unknown')
    state    = session.get('state', 'Unknown')

    if not soil:
        return "मिट्टी का प्रकार चुनें।" if lang == 'hi' else "Error: Soil type not selected."

    if state == 'Unknown':
        for s, ds in STATES_DATA.items():
            if district in ds:
                state = s; session['state'] = s; break

    rec_crop, confidence, reason, reason_hi, alternatives, temp, humidity, rainfall = \
        run_smart_prediction(soil, district, state, season)

    crop_hi      = CROP_HINDI_NAMES.get(rec_crop, "")
    crop_desc    = (CROP_DESCRIPTIONS_HI if lang == 'hi' else CROP_DESCRIPTIONS).get(
                   rec_crop, rec_crop.capitalize())
    cond         = CROP_CONDITIONS.get(rec_crop, {})
    alt_display  = [{"name": a.capitalize(), "emoji": CROP_EMOJIS.get(a, ""),
                     "hindi": CROP_HINDI_NAMES.get(a, "")} for a in alternatives]
    irr          = compute_irrigation_data(rec_crop, rainfall, humidity,
                                           request.form.get('irrigation', 'yes') != 'no')

    if session.get('sms_updates') and session.get('mobile'):
        send_crop_recommendation_sms(
            session['mobile'], rec_crop, crop_hi, district, season, confidence, lang)

    # ── Save to history ───────────────────────────────────────────────────────
    if session.get('mobile'):
        save_recommendation_history(session['mobile'], {
            "datetime":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "activity_type":      "Crop Recommendation",
            "crop":               rec_crop,
            "crop_hindi":         crop_hi,
            "confidence":         confidence,
            "soil":               soil,
            "season":             season,
            "state":              state,
            "district":           district,
            "temperature_c":      round(temp, 1),
            "humidity_pct":       round(humidity, 1),
            "rainfall_mm":        round(rainfall, 1),
            "irrigation_needed_mm": irr["irrigation_added"],
            "irrigation_label":   irr["irr_label_en"],
            "alternatives":       " | ".join(a["name"] for a in alt_display),
            "reason":             reason,
        })

    return render_template("status.html",
        crop=rec_crop, crop_emoji=CROP_EMOJIS.get(rec_crop, ""),
        crop_description=crop_desc, crop_hindi_name=crop_hi,
        temp_range=f"{cond.get('temp',['-','-'])[0]}–{cond.get('temp',['-','-'])[1]}°C",
        humidity_range=f"{cond.get('humidity',['-','-'])[0]}–{cond.get('humidity',['-','-'])[1]}%",
        rainfall_range=f"{cond.get('rainfall',['-','-'])[0]}–{cond.get('rainfall',['-','-'])[1]} mm",
        soil=soil, lang=lang, district=district, state=state, season=season,
        weather=get_weather(district), confidence=confidence,
        reason=reason_hi if lang == 'hi' else reason,
        alternatives=alt_display,
        avg_temp=round(temp,1), avg_humidity=round(humidity,1),
        live_temp=round(temp,1), live_humidity=round(humidity,1), live_rainfall=round(rainfall,1),
        irrigation_available=irr["irrigation_available"],
        irrigation_added=irr["irrigation_added"],
        total_rainfall_15d=irr["total_rainfall_15d"],
        effective_rainfall=irr["effective_rainfall"],
        irr_freq=irr["irr_freq"],
        irr_label=irr["irr_label"] if lang == 'hi' else irr["irr_label_en"],
    )


# ── Analysis AJAX ──────────────────────────────────────────────────────────────
@app.route('/analyse', methods=['POST'])
def analyse():
    data = request.get_json()
    crop = (data.get('crop') or '').strip().lower()
    days = data.get('days', [])
    if not crop or not days:
        return jsonify(error="Missing crop or days"), 400

    day_results = []
    for d in days:
        try: t, h, r = float(d.get('temp',25)), float(d.get('humidity',60)), float(d.get('rainfall',0))
        except: t, h, r = 25.0, 60.0, 0.0
        day_results.append(check_day_suitability(crop, t, h, r))

    good_days  = day_results.count('good')
    total_days = len(day_results)
    status_key, status_en, status_hi = compute_analysis_status(good_days, total_days)

    lang   = session.get('lang', 'en')
    mobile = session.get('mobile')
    if mobile and session.get('sms_updates'):
        crop_hi  = CROP_HINDI_NAMES.get(crop, crop.capitalize())
        district = session.get('district', '')
        try:
            send_sms(mobile,
                f"Kisan Suvidha - Fasal Vishleshan\nFasal: {crop_hi}\nZila: {district}\n"
                f"Sthiti: {status_hi}\nAnukul din: {good_days}/{total_days}"
                if lang == 'hi' else
                f"Kisan Suvidha - Crop Analysis\nCrop: {crop.capitalize()}\n"
                f"District: {district}\nStatus: {status_en}\n"
                f"Suitable days: {good_days}/{total_days}"
            )
        except: pass

    # ── Save to history ───────────────────────────────────────────────────────
    if session.get('mobile'):
        save_analysis_history(session['mobile'], {
            "datetime":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "activity_type":  "Crop Analysis",
            "crop":           crop,
            "district":       session.get('district', ''),
            "total_days":     total_days,
            "good_days":      good_days,
            "bad_days":       total_days - good_days,
            "overall_status": status_en,
            "day_results":    " | ".join(day_results),
        })

    return jsonify(day_results=day_results, good_days=good_days, total_days=total_days,
                   status_key=status_key, status_en=status_en, status_hi=status_hi)


# ── Support ────────────────────────────────────────────────────────────────────
@app.route('/support')
def support():
    lang = request.args.get('lang') or session.get('lang', 'en')
    session['lang'] = lang
    return render_template('support.html', lang=lang)


@app.route('/submit_support', methods=['POST'])
def submit_support():
    name    = request.form.get('name', '')
    email   = request.form.get('email', '')
    message = request.form.get('message', '')
    try:
        msg = Message(subject=f"Kisan Support – {name}",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=['shubhsoni1244@gmail.com'])
        msg.body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        mail.send(msg)
        return ("<h2 style='color:green;text-align:center;'>Message Sent!</h2>"
                "<div style='text-align:center'><a href='/support'><button>Back</button></a></div>")
    except Exception as e:
        return (f"<h2 style='color:red;text-align:center;'>Error: {e}</h2>"
                "<div style='text-align:center'><a href='/support'><button>Try Again</button></a></div>")


# ── Schemes ────────────────────────────────────────────────────────────────────
@app.route('/schemes')
def schemes():
    lang = request.args.get('lang') or session.get('lang', 'en')
    session['lang'] = lang
    if lang == 'hi':
        schemes_data = [
            {"name":"पीएम-किसान योजना","desc":"किसानों को प्रति वर्ष ₹6000 की वित्तीय सहायता।","link":"https://pmkisan.gov.in/"},
            {"name":"प्रधानमंत्री फसल बीमा योजना","desc":"प्राकृतिक आपदा से फसल नुकसान पर बीमा।","link":"https://pmfby.gov.in/"},
            {"name":"मृदा स्वास्थ्य कार्ड योजना","desc":"मिट्टी परीक्षण रिपोर्ट निःशुल्क।","link":"https://soilhealth.dac.gov.in/"},
            {"name":"किसान क्रेडिट कार्ड","desc":"कम ब्याज पर खेती के लिए ऋण।","link":"https://www.nabard.org/"},
            {"name":"ई-नाम","desc":"ऑनलाइन कृषि व्यापार मंच।","link":"https://www.enam.gov.in/"},
        ]
    else:
        schemes_data = [
            {"name":"PM-KISAN Scheme","desc":"Rs. 6,000/year financial support to farmer families.","link":"https://pmkisan.gov.in/"},
            {"name":"PM Fasal Bima Yojana","desc":"Crop insurance against natural calamities.","link":"https://pmfby.gov.in/"},
            {"name":"Soil Health Card","desc":"Free soil test reports for better fertiliser use.","link":"https://soilhealth.dac.gov.in/"},
            {"name":"Kisan Credit Card","desc":"Low-interest credit for farming needs.","link":"https://www.nabard.org/"},
            {"name":"e-NAM","desc":"National Agriculture Market - online trading portal.","link":"https://www.enam.gov.in/"},
        ]
    return render_template("schemes.html", schemes=schemes_data, lang=lang)


@app.route('/status', methods=['POST'])
def status():
    return "Status recorded."


# ── Logout ────────────────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    from flask import redirect, url_for
    session.clear()
    return redirect(url_for('home'))


# ── History page ──────────────────────────────────────────────────────────────
@app.route('/history')
def history():
    from flask import redirect, url_for
    mobile = session.get('mobile')
    if not mobile:
        return redirect(url_for('login'))
    lang    = request.args.get('lang') or session.get('lang', 'en')
    session['lang'] = lang
    records = load_user_history(mobile)
    return render_template('history.html',
                           lang=lang,
                           name=session.get('name', ''),
                           district=session.get('district', ''),
                           records=records)


if __name__ == '__main__':
    app.run(debug=True)
