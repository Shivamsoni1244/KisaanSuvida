import json
from datetime import datetime

# ── Load JSON data files ───────────────────────────────────────────────────────
with open("states-and-districts.json") as f:
    STATES_DATA = json.load(f)

STATES = list(STATES_DATA.keys())

with open("crop_conditions.json") as f:
    CROP_CONDITIONS = json.load(f)

with open("state_crops.json") as f:
    STATE_CROPS = json.load(f)

with open("seasonal_rainfall.json") as f:
    SEASONAL_RAINFALL = json.load(f)

# ── Crop emojis ────────────────────────────────────────────────────────────────
CROP_EMOJIS = {
    "rice": "🍚", "maize": "🌽", "chickpea": "🫘", "kidneybeans": "🫘",
    "pigeonpeas": "🌿", "mothbeans": "🫘", "mungbean": "🟢", "blackgram": "⚫",
    "lentil": "🫘", "pomegranate": "🍎", "banana": "🍌", "mango": "🥭",
    "grapes": "🍇", "watermelon": "🍉", "muskmelon": "🍈", "apple": "🍎",
    "orange": "🍊", "papaya": "🍑", "coconut": "🥥", "cotton": "☁️",
    "jute": "🌱", "coffee": "☕"
}

# ── Crop Hindi names ───────────────────────────────────────────────────────────
CROP_HINDI_NAMES = {
    "rice":        "चावल",
    "maize":       "मक्का",
    "chickpea":    "चना",
    "kidneybeans": "राजमा",
    "pigeonpeas":  "अरहर",
    "mothbeans":   "मोठ",
    "mungbean":    "मूंग",
    "blackgram":   "उड़द",
    "lentil":      "मसूर",
    "pomegranate": "अनार",
    "banana":      "केला",
    "mango":       "आम",
    "grapes":      "अंगूर",
    "watermelon":  "तरबूज",
    "muskmelon":   "खरबूजा",
    "apple":       "सेब",
    "orange":      "संतरा",
    "papaya":      "पपीता",
    "coconut":     "नारियल",
    "cotton":      "कपास",
    "jute":        "जूट",
    "coffee":      "कॉफी"
}

# ── Crop descriptions (English) ────────────────────────────────────────────────
CROP_DESCRIPTIONS = {
    "rice": (
        "Rice is a staple cereal crop that thrives in warm, humid climates with abundant water. "
        "It is the primary food source for over half the world's population and grows best in "
        "waterlogged or flooded paddy fields. Rice requires temperatures between 20–35°C, heavy "
        "rainfall or continuous irrigation, and fertile clay or loamy soils. It is cultivated "
        "across all major states in India during the Kharif season and supports millions of farming "
        "families. Common varieties include Basmati, Sona Masuri, and IR-36."
    ),
    "maize": (
        "Maize (corn) is a versatile cereal crop used for food, fodder, starch, and industrial "
        "purposes. It grows rapidly in warm weather and requires well-drained fertile soil with "
        "moderate rainfall of 60–110 mm per month. Maize is sensitive to frost and waterlogging. "
        "It is grown in Kharif season across Bihar, Uttar Pradesh, Karnataka, and Rajasthan. "
        "Modern hybrid varieties yield 5–8 tonnes per hectare. Maize is also a key ingredient "
        "in animal feed and is increasingly used for ethanol production."
    ),
    "chickpea": (
        "Chickpea is a cool-season legume rich in protein and fiber. It fixes atmospheric nitrogen "
        "in the soil, improving fertility for the next crop. Highly drought-tolerant, it is ideal "
        "for dry Rabi seasons in semi-arid regions. Chickpea grows best at 15–25°C in well-drained "
        "loamy soils with low humidity. Madhya Pradesh, Rajasthan, Maharashtra, and Uttar Pradesh "
        "are the top producers. It is a crucial pulse crop for protein nutrition in rural India "
        "and is used in dal, besan, and snacks."
    ),
    "kidneybeans": (
        "Kidney beans are a protein-rich legume that prefer cool to mild temperatures between 15–25°C. "
        "They improve soil fertility through nitrogen fixation and grow well in well-drained loamy soils. "
        "Kidney beans require moderate rainfall and are sensitive to waterlogging. They are extensively "
        "grown in Jammu & Kashmir, Himachal Pradesh, and Uttarakhand. Known as 'Rajma' in India, they "
        "are a staple in North Indian cuisine. The crop matures in 90–120 days and yields 1–2 tonnes "
        "per hectare under good management."
    ),
    "pigeonpeas": (
        "Pigeon peas (Tur/Arhar) are a drought-tolerant legume widely grown in tropical and semi-arid "
        "regions. They are nitrogen-fixing, improve soil health, and serve as both food and fodder. "
        "Pigeon peas can grow in poor soils with minimal rainfall and tolerate high temperatures up to "
        "37°C. Maharashtra, Uttar Pradesh, Karnataka, and Andhra Pradesh are major producers. "
        "The crop takes 150–180 days to mature and is a key source of protein in Indian dals. "
        "Its woody stems are used as fuel and its pods as fodder."
    ),
    "mothbeans": (
        "Moth beans are extremely drought-resistant and grow in arid, sandy soils where few other crops "
        "survive. They are a key pulse crop in Rajasthan and Gujarat, thriving in temperatures up to "
        "40°C with very little water (30–75 mm/month). Moth beans enrich the soil with nitrogen and "
        "mature quickly in 60–90 days. The seeds are used to make dal, sprouts, and fermented foods. "
        "They are an important food security crop in desert regions and provide nutritious animal feed "
        "through their leaves and pods."
    ),
    "mungbean": (
        "Mung beans (green gram / moong) are a short-duration, warm-season legume. They are highly "
        "nutritious, quick to mature (60–75 days), and improve soil structure through nitrogen fixation. "
        "Mung beans grow best at 27–30°C with moderate to high humidity. They are sensitive to "
        "waterlogging and require well-drained loamy soils. Grown in both Kharif and Zaid seasons "
        "across Rajasthan, Maharashtra, and Andhra Pradesh. Moong dal is one of the most digestible "
        "legumes and is widely consumed in Indian households."
    ),
    "blackgram": (
        "Black gram (Urad dal) is a warm-season legume popular throughout India and essential to "
        "South Indian cuisine. It thrives in humid tropical conditions at 25–35°C and is tolerant "
        "of moderate drought. Black gram improves soil fertility through nitrogen fixation. "
        "It is grown during Kharif in Andhra Pradesh, Tamil Nadu, Madhya Pradesh, and Uttar Pradesh. "
        "The crop matures in 70–90 days and yields 0.8–1.5 tonnes/hectare. It is the key ingredient "
        "in idli, dosa, vada, and various dals — making it indispensable in Indian kitchens."
    ),
    "lentil": (
        "Lentils (Masoor dal) are a cool-season legume cultivated for their edible seeds. They are "
        "drought-tolerant, nitrogen-fixing, and grow best in light, well-drained soils with moderate "
        "moisture at 18–30°C. Lentils are primarily a Rabi crop grown in Uttar Pradesh, Madhya Pradesh, "
        "Bihar, and West Bengal. The crop matures in 100–120 days and yields 0.8–1.5 tonnes/hectare. "
        "Rich in protein, iron, and folate, lentils are among the oldest cultivated crops in the world "
        "and form a vital part of the daily Indian diet."
    ),
    "pomegranate": (
        "Pomegranate is a hardy fruit tree that tolerates drought and high temperatures, making it "
        "ideal for semi-arid and arid climates. It grows well in well-drained soils at 18–25°C and "
        "requires low humidity for quality fruit development. Maharashtra (Solapur), Karnataka, "
        "Gujarat, and Rajasthan are major producing states. The fruit is rich in antioxidants, "
        "vitamins C and K, and folate. A single tree bears fruit for 15–20 years. Pomegranate "
        "commands premium prices in both domestic and export markets."
    ),
    "banana": (
        "Banana is a tropical fruit crop that requires warm temperatures (25–30°C), high humidity, "
        "and plenty of water. It grows year-round in fertile, well-drained soils and produces fruit "
        "continuously. India is the world's largest banana producer, with Andhra Pradesh, Tamil Nadu, "
        "Karnataka, Gujarat, and Maharashtra as top states. Banana plants mature in 9–12 months "
        "and produce large bunches of 100–200 fruits. Rich in potassium, Vitamin B6, and fiber, "
        "bananas are among India's most important and widely consumed fruits."
    ),
    "mango": (
        "Mango is India's national fruit and the 'King of Fruits'. It thrives in hot, dry weather "
        "during flowering and fruiting and prefers deep, well-drained alluvial soils. Mango trees "
        "need temperatures of 27–36°C and are sensitive to frost. Uttar Pradesh, Andhra Pradesh, "
        "Karnataka, Bihar, and Gujarat are major producers. Varieties like Alphonso, Dasheri, Langra, "
        "and Kesar have global recognition. A mango tree can produce fruit for 40–50 years, making "
        "it a long-term investment for farmers. India exports mangoes to over 40 countries."
    ),
    "grapes": (
        "Grapes are a climbing fruit crop grown in a wide range of climates (9–42°C). They prefer "
        "dry summers and mild winters, requiring well-drained sandy loam soils for best fruit quality. "
        "Maharashtra (Nashik) accounts for over 80% of India's grape production, followed by "
        "Karnataka and Andhra Pradesh. Grapes are harvested in February–May. They are consumed "
        "fresh and used to produce wine, raisins, and juice. Indian grapes are exported to the UK, "
        "Netherlands, and the Middle East. The crop requires careful management of irrigation, "
        "pruning, and disease control."
    ),
    "watermelon": (
        "Watermelon is a warm-season fruit that grows best in hot, dry climates with plenty of "
        "sunlight at 24–27°C. It needs sandy loam soil, good drainage, and consistent drip irrigation. "
        "Watermelon is a Zaid crop grown from March to June across Uttar Pradesh, Andhra Pradesh, "
        "Tamil Nadu, and West Bengal. It matures in just 70–90 days and can yield 20–30 tonnes/hectare. "
        "Rich in water content (92%), lycopene, and Vitamin C, it is a popular summer crop that "
        "fetches good market prices due to high demand in the hot season."
    ),
    "muskmelon": (
        "Muskmelon (Cantaloupe / Kharbooja) thrives in hot, dry weather with low humidity at 27–30°C. "
        "It requires well-drained sandy soil and lots of sunshine to develop its characteristic sweet "
        "flavour and fragrance. Muskmelon is grown in Zaid season across Uttar Pradesh, Punjab, "
        "Rajasthan, and Maharashtra. It matures in 75–100 days. The fruit is rich in Vitamin A, C, "
        "and potassium. Its high water content makes it a refreshing summer crop. Low rainfall "
        "requirement (20–30 mm/month) makes it perfect for regions with limited irrigation."
    ),
    "apple": (
        "Apple is a temperate fruit crop requiring cool winters (chilling hours below 7°C) for "
        "dormancy and moderate temperatures (21–24°C) during fruit development. It grows best in "
        "hilly regions like Himachal Pradesh, Jammu & Kashmir, and Uttarakhand. The Shimla apple "
        "is world-famous for its taste and quality. Apple orchards require well-drained loamy soils "
        "with good organic matter. A well-managed orchard can yield 20–30 tonnes/hectare and remain "
        "productive for 30–40 years. Apple farming is one of the most profitable enterprises in "
        "hill-state agriculture."
    ),
    "orange": (
        "Oranges are subtropical citrus fruits that need a mild climate (10–35°C) with distinct dry "
        "and wet seasons. They grow best in well-drained soils and require full sunlight for optimum "
        "fruit quality and sweetness. Nagpur (Maharashtra) is the 'Orange City' of India and a "
        "world-famous production centre. Other key states include Punjab, Himachal Pradesh, "
        "Rajasthan, and Meghalaya. Rich in Vitamin C, oranges boost immunity and are consumed "
        "fresh, juiced, and processed. India exports oranges to Bangladesh, Nepal, and the Gulf. "
        "The crop takes 3–5 years from planting to first fruit."
    ),
    "papaya": (
        "Papaya is a fast-growing tropical fruit that produces fruit year-round in warm, humid "
        "conditions at 23–44°C. It is sensitive to frost and waterlogging but grows quickly in "
        "fertile, well-drained soils. Papaya starts bearing fruit within 6–9 months of planting. "
        "Andhra Pradesh, Karnataka, Gujarat, and West Bengal are top producers. Rich in Vitamin C, "
        "folate, and the enzyme papain, papaya supports digestion and immunity. It is also used "
        "in the pharmaceutical industry. A single papaya plant can produce 30–50 kg of fruit per year."
    ),
    "coconut": (
        "Coconut palm is a tropical coastal crop that thrives in hot, humid conditions at 25–30°C "
        "with very high humidity (90–100%). It tolerates saline soils and strong winds, making it "
        "ideal for India's coastal belts. Kerala is the top producer, followed by Karnataka, Tamil "
        "Nadu, and Andhra Pradesh. Every part of the coconut tree has economic value — the fruit "
        "provides water, milk, oil, and copra; leaves are used for thatching; trunk for timber. "
        "A coconut tree begins bearing fruit in 6–10 years and can produce for over 60 years, "
        "making it one of the most valuable perennial crops in India."
    ),
    "cotton": (
        "Cotton is India's most important fibre crop and a backbone of the textile industry. "
        "It grows in warm, semi-arid conditions at 22–26°C, requiring a long frost-free season "
        "of at least 180 days. Heavy black (regur) soils of Maharashtra, Gujarat, and Telangana "
        "are ideal. India is the world's largest producer of cotton. The crop needs moderate "
        "rainfall (60–100 mm/month) and is sensitive to excess moisture. Bt cotton has "
        "dramatically increased yields. Cotton farming supports over 60 million farmers and "
        "textile workers. The bolls take 150–180 days to mature after sowing."
    ),
    "jute": (
        "Jute is the 'Golden Fibre' of India and the second most important fibre crop after cotton. "
        "It grows in warm, humid climates at 23–27°C with heavy rainfall (150–200 mm/month). "
        "Jute thrives in alluvial flood plains of the Ganges delta. West Bengal and Assam produce "
        "over 90% of India's jute. The crop matures in 120–150 days and grows up to 3–4 metres tall. "
        "Jute is used to make sacks, rope, carpet, and eco-friendly packaging. Being 100% biodegradable "
        "and carbon-neutral, jute farming is increasingly valued in the era of sustainable development."
    ),
    "coffee": (
        "Coffee is a tropical plantation crop grown in hilly regions with high rainfall and moderate "
        "temperatures of 23–28°C. India grows both Arabica (milder, grown at higher altitudes) and "
        "Robusta (stronger, grown at lower altitudes). Karnataka (Coorg, Chikmagalur) produces "
        "over 70% of India's coffee, followed by Kerala and Tamil Nadu. Coffee plants take 3–5 years "
        "to start bearing berries and remain productive for 20–30 years. Indian coffee is celebrated "
        "globally for its distinct flavour profiles. Coffee requires shade trees, well-drained forest "
        "soils, and high humidity (85–95%) to thrive."
    ),
}

# ── Crop descriptions (Hindi) ──────────────────────────────────────────────────
CROP_DESCRIPTIONS_HI = {
    "rice": (
        "चावल एक मुख्य अनाज फसल है जो गर्म और आर्द्र जलवायु में खूब पानी के साथ फलती-फूलती है। "
        "यह दुनिया की आधी से अधिक आबादी का प्राथमिक भोजन स्रोत है और जलमग्न धान के खेतों में "
        "सबसे अच्छी तरह उगती है। चावल के लिए 20–35°C तापमान, भारी वर्षा या निरंतर सिंचाई, "
        "और उपजाऊ चिकनी या दोमट मिट्टी आवश्यक है। खरीफ मौसम में भारत के सभी प्रमुख राज्यों में "
        "इसकी खेती होती है। बासमती, सोना मसूरी और IR-36 इसकी प्रमुख किस्में हैं।"
    ),
    "maize": (
        "मक्का एक बहुउपयोगी अनाज फसल है जिसका उपयोग भोजन, पशुचारा, स्टार्च और उद्योग में होता है। "
        "यह गर्म मौसम में तेज़ी से बढ़ती है और 60–110 मिमी मासिक वर्षा के साथ उपजाऊ, अच्छी जल "
        "निकासी वाली मिट्टी में पनपती है। मक्का पाले और जलभराव से बहुत संवेदनशील है। "
        "बिहार, उत्तर प्रदेश, कर्नाटक और राजस्थान में खरीफ मौसम में उगाई जाती है। "
        "आधुनिक हाइब्रिड किस्में 5–8 टन प्रति हेक्टेयर उपज देती हैं।"
    ),
    "chickpea": (
        "चना (छोले) एक ठंडे मौसम की दलहन फसल है जो प्रोटीन और फाइबर से भरपूर है। "
        "यह मिट्टी में वायुमंडलीय नाइट्रोजन स्थिर करती है और अगली फसल के लिए उर्वरता बढ़ाती है। "
        "अत्यधिक सूखा-सहिष्णु, यह अर्ध-शुष्क क्षेत्रों की रबी फसल के लिए आदर्श है। "
        "15–25°C तापमान और कम आर्द्रता में अच्छी जल निकासी वाली दोमट मिट्टी में उगती है। "
        "मध्य प्रदेश, राजस्थान, महाराष्ट्र और उत्तर प्रदेश प्रमुख उत्पादक राज्य हैं।"
    ),
    "kidneybeans": (
        "राजमा एक प्रोटीनयुक्त दलहन है जो 15–25°C के ठंडे तापमान में पनपती है। "
        "यह नाइट्रोजन स्थिरीकरण के माध्यम से मिट्टी की उर्वरता बढ़ाती है और अच्छी जल निकासी "
        "वाली दोमट मिट्टी में अच्छी तरह उगती है। जम्मू-कश्मीर, हिमाचल प्रदेश और उत्तराखंड में "
        "बड़े पैमाने पर उगाई जाती है। 90–120 दिनों में पकती है और 1–2 टन/हेक्टेयर उपज देती है। "
        "राजमा उत्तर भारतीय रसोई का एक अनिवार्य हिस्सा है।"
    ),
    "pigeonpeas": (
        "अरहर (तुअर दाल) एक सूखा-सहिष्णु दलहन है जो उष्णकटिबंधीय और अर्ध-शुष्क क्षेत्रों में "
        "उगाई जाती है। यह नाइट्रोजन स्थिर करती है, मिट्टी स्वास्थ्य सुधारती है, और भोजन तथा "
        "पशुचारा दोनों के रूप में काम आती है। खराब मिट्टी में भी कम वर्षा से उग सकती है और "
        "37°C तक तापमान सहन कर सकती है। महाराष्ट्र, उत्तर प्रदेश, कर्नाटक और आंध्र प्रदेश "
        "प्रमुख उत्पादक हैं। फसल 150–180 दिनों में पकती है।"
    ),
    "mothbeans": (
        "मोठ (मठ बींस) अत्यधिक सूखा-प्रतिरोधी हैं और शुष्क, रेतीली मिट्टी में उगती हैं जहाँ "
        "अन्य फसलें जीवित नहीं रह सकतीं। राजस्थान और गुजरात में यह एक प्रमुख दलहन फसल है, "
        "जो 40°C तक तापमान और बहुत कम पानी (30–75 मिमी/माह) में पनपती है। "
        "मोठ मिट्टी को नाइट्रोजन से समृद्ध करती है और 60–90 दिनों में पक जाती है। "
        "रेगिस्तानी क्षेत्रों में खाद्य सुरक्षा के लिए यह एक महत्वपूर्ण फसल है।"
    ),
    "mungbean": (
        "मूंग (हरा चना / मूंग दाल) एक कम अवधि की गर्म मौसम की दलहन फसल है। "
        "यह अत्यधिक पौष्टिक, जल्दी पकने वाली (60–75 दिन) और नाइट्रोजन स्थिरीकरण के माध्यम से "
        "मिट्टी संरचना में सुधार करने वाली है। 27–30°C और मध्यम से अधिक आर्द्रता में अच्छी "
        "तरह बढ़ती है। जलभराव से संवेदनशील है। राजस्थान, महाराष्ट्र और आंध्र प्रदेश में खरीफ "
        "और जायद दोनों मौसमों में उगाई जाती है।"
    ),
    "blackgram": (
        "उड़द (काला चना) एक गर्म मौसम की दलहन फसल है जो पूरे भारत में लोकप्रिय है और "
        "दक्षिण भारतीय व्यंजनों के लिए अनिवार्य है। यह 25–35°C की आर्द्र उष्णकटिबंधीय "
        "परिस्थितियों में पनपती है। आंध्र प्रदेश, तमिलनाडु, मध्य प्रदेश और उत्तर प्रदेश में "
        "खरीफ के दौरान उगाई जाती है। फसल 70–90 दिनों में पकती है। "
        "इडली, डोसा, वड़ा और विभिन्न दालों में इसका उपयोग होता है।"
    ),
    "lentil": (
        "मसूर दाल एक ठंडे मौसम की दलहन है जो खाद्य बीजों के लिए उगाई जाती है। "
        "यह सूखा-सहिष्णु, नाइट्रोजन-स्थिरीकरण करने वाली और 18–30°C पर हल्की, अच्छी जल निकासी "
        "वाली मिट्टी में मध्यम नमी के साथ सबसे अच्छी तरह उगती है। उत्तर प्रदेश, मध्य प्रदेश, "
        "बिहार और पश्चिम बंगाल में यह रबी की प्रमुख फसल है। 100–120 दिनों में पकती है। "
        "प्रोटीन, आयरन और फोलेट से भरपूर मसूर दुनिया की सबसे पुरानी खेती की जाने वाली फसलों में से एक है।"
    ),
    "pomegranate": (
        "अनार एक कठोर फल वृक्ष है जो सूखे और उच्च तापमान को सहन करता है, जिससे यह अर्ध-शुष्क "
        "जलवायु के लिए आदर्श है। 18–25°C पर अच्छी जल निकासी वाली मिट्टी में उगता है और गुणवत्तापूर्ण "
        "फल के लिए कम आर्द्रता चाहिए। महाराष्ट्र (सोलापुर), कर्नाटक, गुजरात और राजस्थान "
        "प्रमुख उत्पादक राज्य हैं। एक वृक्ष 15–20 वर्ष तक फल देता है। "
        "एंटीऑक्सीडेंट और विटामिन C से भरपूर यह फल घरेलू और निर्यात दोनों बाजारों में अच्छे दाम पाता है।"
    ),
    "banana": (
        "केला एक उष्णकटिबंधीय फल फसल है जिसे गर्म तापमान (25–30°C), उच्च आर्द्रता और "
        "पर्याप्त पानी की आवश्यकता होती है। उपजाऊ, अच्छी जल निकासी वाली मिट्टी में साल भर "
        "फल देती है। भारत दुनिया का सबसे बड़ा केला उत्पादक है। आंध्र प्रदेश, तमिलनाडु, "
        "कर्नाटक, गुजरात और महाराष्ट्र शीर्ष राज्य हैं। केले के पौधे 9–12 महीनों में पकते हैं "
        "और 100–200 फलों के बड़े गुच्छे देते हैं। पोटेशियम और विटामिन B6 से भरपूर।"
    ),
    "mango": (
        "आम भारत का राष्ट्रीय फल है और 'फलों का राजा' है। फूल और फल आने के दौरान गर्म, "
        "शुष्क मौसम में पनपता है और 27–36°C तापमान पर गहरी, अच्छी जल निकासी वाली जलोढ़ मिट्टी "
        "पसंद करता है। उत्तर प्रदेश, आंध्र प्रदेश, कर्नाटक, बिहार और गुजरात प्रमुख उत्पादक हैं। "
        "अल्फांसो, दशहरी, लंगड़ा और केसर जैसी किस्मों की वैश्विक पहचान है। "
        "एक आम का पेड़ 40–50 वर्षों तक फल देता है।"
    ),
    "grapes": (
        "अंगूर एक चढ़ने वाली फल फसल है जो विभिन्न जलवायु (9–42°C) में उगती है। "
        "इसे शुष्क गर्मी और हल्की सर्दी पसंद है, और गुणवत्तापूर्ण फल के लिए अच्छी जल निकासी "
        "वाली बलुई दोमट मिट्टी चाहिए। महाराष्ट्र (नासिक) भारत के 80% से अधिक अंगूर उत्पादन के "
        "लिए जिम्मेदार है। फरवरी–मई में कटाई होती है। ताजा खाने के अलावा शराब, किशमिश और "
        "जूस के लिए उपयोग होता है।"
    ),
    "watermelon": (
        "तरबूज एक गर्म मौसम का फल है जो 24–27°C में खूब धूप के साथ सबसे अच्छा उगता है। "
        "इसे बलुई दोमट मिट्टी, अच्छी जल निकासी और नियमित ड्रिप सिंचाई की आवश्यकता है। "
        "मार्च से जून के बीच जायद फसल के रूप में उत्तर प्रदेश, आंध्र प्रदेश, "
        "तमिलनाडु और पश्चिम बंगाल में उगाया जाता है। 70–90 दिनों में पक जाता है। "
        "92% जलांश, लाइकोपीन और विटामिन C से भरपूर यह गर्मियों की लोकप्रिय फसल है।"
    ),
    "muskmelon": (
        "खरबूजा 27–30°C के गर्म, शुष्क मौसम और कम आर्द्रता में पनपता है। "
        "अपनी विशिष्ट मिठास और सुगंध के लिए अच्छी जल निकासी वाली बलुई मिट्टी और "
        "भरपूर धूप चाहिए। उत्तर प्रदेश, पंजाब, राजस्थान और महाराष्ट्र में जायद मौसम में उगाया जाता है। "
        "75–100 दिनों में पकता है। विटामिन A, C और पोटेशियम से भरपूर। "
        "कम वर्षा (20–30 मिमी/माह) की जरूरत सीमित सिंचाई वाले क्षेत्रों के लिए आदर्श बनाती है।"
    ),
    "apple": (
        "सेब एक शीतोष्ण फल फसल है जिसे निष्क्रियता के लिए ठंडी सर्दी (7°C से नीचे) और "
        "फल विकास के दौरान 21–24°C तापमान चाहिए। हिमाचल प्रदेश, जम्मू-कश्मीर और उत्तराखंड "
        "के पहाड़ी क्षेत्रों में सबसे अच्छा उगता है। शिमला सेब अपने स्वाद और गुणवत्ता के लिए "
        "विश्व प्रसिद्ध है। अच्छे प्रबंधन के साथ एक बाग 20–30 टन/हेक्टेयर उपज दे सकता है। "
        "सेब बागान 30–40 वर्षों तक उत्पादक रहता है।"
    ),
    "orange": (
        "संतरा एक उपोष्णकटिबंधीय खट्टे फल है जिसे 10–35°C के हल्के जलवायु और शुष्क-आर्द्र "
        "मौसम की अलग-अलग ऋतुओं की जरूरत है। नागपुर (महाराष्ट्र) को 'संतरों का शहर' कहा जाता है। "
        "पंजाब, हिमाचल प्रदेश, राजस्थान और मेघालय भी प्रमुख उत्पादक हैं। "
        "विटामिन C से भरपूर संतरे रोग प्रतिरोधक क्षमता बढ़ाते हैं। "
        "भारत बांग्लादेश, नेपाल और खाड़ी देशों को संतरे निर्यात करता है।"
    ),
    "papaya": (
        "पपीता एक तेज़ी से बढ़ने वाला उष्णकटिबंधीय फल है जो 23–44°C में गर्म, आर्द्र परिस्थितियों "
        "में साल भर फल देता है। यह पाले और जलभराव के प्रति संवेदनशील है। रोपण के 6–9 महीनों में "
        "फल देना शुरू कर देता है। आंध्र प्रदेश, कर्नाटक, गुजरात और पश्चिम बंगाल शीर्ष उत्पादक हैं। "
        "विटामिन C, फोलेट और पपेन एंजाइम से भरपूर पपीता पाचन और रोग प्रतिरोधक क्षमता के लिए "
        "लाभदायक है। एक पौधा प्रति वर्ष 30–50 किग्रा फल दे सकता है।"
    ),
    "coconut": (
        "नारियल का पेड़ एक उष्णकटिबंधीय तटीय फसल है जो 25–30°C और बहुत अधिक आर्द्रता (90–100%) "
        "में पनपता है। यह खारी मिट्टी और तेज़ हवाओं को सहन करता है, जिससे यह भारत के तटीय क्षेत्रों "
        "के लिए आदर्श है। केरल शीर्ष उत्पादक है, इसके बाद कर्नाटक, तमिलनाडु और आंध्र प्रदेश हैं। "
        "नारियल के पेड़ का हर भाग आर्थिक मूल्य रखता है। "
        "एक पेड़ 6–10 वर्षों में फल देना शुरू करता है और 60 से अधिक वर्षों तक उत्पादन करता है।"
    ),
    "cotton": (
        "कपास भारत की सबसे महत्वपूर्ण रेशा फसल है और वस्त्र उद्योग की रीढ़ है। "
        "यह 22–26°C के गर्म, अर्ध-शुष्क परिस्थितियों में उगती है और कम से कम 180 दिनों के "
        "पाले-मुक्त मौसम की आवश्यकता है। महाराष्ट्र, गुजरात और तेलंगाना की भारी काली मिट्टी आदर्श है। "
        "भारत दुनिया का सबसे बड़ा कपास उत्पादक है। 6 करोड़ से अधिक किसानों और "
        "वस्त्र मजदूरों की आजीविका इस फसल पर निर्भर है।"
    ),
    "jute": (
        "जूट भारत का 'सुनहरा रेशा' है और कपास के बाद दूसरी सबसे महत्वपूर्ण रेशा फसल है। "
        "यह 23–27°C और भारी वर्षा (150–200 मिमी/माह) में उगती है। "
        "पश्चिम बंगाल और असम भारत के 90% से अधिक जूट का उत्पादन करते हैं। "
        "फसल 120–150 दिनों में पकती है और 3–4 मीटर ऊँची होती है। "
        "बोरे, रस्सी, कालीन और पर्यावरण अनुकूल पैकेजिंग में उपयोग होता है। "
        "100% जैवनिम्नीकरणीय होने के कारण यह टिकाऊ विकास के युग में और भी मूल्यवान है।"
    ),
    "coffee": (
        "कॉफी एक उष्णकटिबंधीय बागान फसल है जो पहाड़ी क्षेत्रों में 23–28°C तापमान और "
        "उच्च वर्षा के साथ उगती है। भारत में अरेबिका (हल्की, ऊँचाई पर) और रोबस्टा "
        "(मजबूत, कम ऊँचाई पर) दोनों किस्में उगाई जाती हैं। कर्नाटक (कूर्ग, चिकमगलूर) "
        "भारत की 70% से अधिक कॉफी उत्पादन करता है, इसके बाद केरल और तमिलनाडु आते हैं। "
        "कॉफी के पौधे 3–5 वर्षों में फल देना शुरू करते हैं और 20–30 वर्षों तक उत्पादक रहते हैं। "
        "भारतीय कॉफी अपने अद्वितीय स्वाद के लिए वैश्विक स्तर पर प्रसिद्ध है।"
    ),
}

# ── Season → valid crops ───────────────────────────────────────────────────────
SEASON_CROPS = {
    "Kharif": [
        "rice", "maize", "cotton", "jute", "pigeonpeas",
        "mungbean", "blackgram", "banana", "papaya", "coconut"
    ],
    "Rabi": [
        "wheat", "chickpea", "lentil", "kidneybeans", "mustard",
        "peas", "mango", "orange", "grapes", "pomegranate", "apple"
    ],
    "Zaid": [
        "watermelon", "muskmelon", "mungbean", "maize",
        "mothbeans", "cucumber", "sunflower"
    ]
}

# ── Soil → suitable crops ──────────────────────────────────────────────────────
SOIL_CROPS = {
    "Alluvial":  ["rice", "wheat", "maize", "sugarcane", "jute", "banana",
                  "mango", "lentil", "chickpea", "mungbean", "blackgram"],
    "Black":     ["cotton", "sorghum", "wheat", "sugarcane", "maize",
                  "sunflower", "grapes", "chickpea", "pigeonpeas"],
    "Red":       ["maize", "millet", "groundnut", "pigeonpeas", "blackgram",
                  "mungbean", "banana", "papaya", "mango", "coffee"],
    "Laterite":  ["rice", "coconut", "banana", "coffee", "tea",
                  "cashew", "papaya", "blackgram"],
    "Desert":    ["mothbeans", "maize", "mustard", "pomegranate",
                  "watermelon", "muskmelon", "mung"],
    "Mountain":  ["apple", "maize", "wheat", "orange", "ginger",
                  "potato", "kidneybeans", "rice"],
    "Saline":    ["rice", "coconut", "sugarcane"],
    "Peaty":     ["rice", "jute", "banana", "blackgram"],
}

# ── Soil NPK + pH values ───────────────────────────────────────────────────────
SOIL_VALUES = {
    "Alluvial": (90, 45, 45, 6.5),
    "Black":    (75, 38, 38, 7.5),
    "Red":      (35, 18, 18, 5.8),
    "Laterite": (25, 12, 12, 5.2),
    "Desert":   (15,  8,  8, 8.2),
    "Mountain": (55, 30, 30, 6.0),
    "Saline":   (20,  8, 12, 8.8),
    "Peaty":    (95, 45, 45, 4.8),
}

# ── Helper functions ───────────────────────────────────────────────────────────

def get_current_season():
    month = datetime.now().month
    if month in [10, 11, 12, 1, 2, 3]:
        return "Rabi"
    elif month in [6, 7, 8, 9]:
        return "Kharif"
    return "Zaid"


def get_soil_values(soil):
    """Returns (N, P, K, pH) for the given soil type."""
    values = SOIL_VALUES.get(soil, (50, 25, 25, 6.5))
    print(f"Soil values → {soil}: N={values[0]} P={values[1]} K={values[2]} pH={values[3]}")
    return values


def get_state_valid_crops(state):
    return STATE_CROPS.get(state, list(CROP_CONDITIONS.keys()))


def get_season_valid_crops(season):
    return SEASON_CROPS.get(season, list(CROP_CONDITIONS.keys()))


def get_soil_valid_crops(soil):
    return SOIL_CROPS.get(soil, list(CROP_CONDITIONS.keys()))


def score_crop_against_weather(crop, temp, humidity, rainfall):
    """
    Closeness score — lower is better.
    Uses soft scoring: 0 if within range, scaled penalty outside range.
    Temperature is weighted highest (2x) as it is the most critical factor.
    Humidity and rainfall get partial credit when close to the boundary.
    """
    cond = CROP_CONDITIONS.get(crop)
    if not cond:
        return 9999
    t_min, t_max = cond['temp']
    h_min, h_max = cond['humidity']
    r_min, r_max = cond['rainfall']

    def soft_penalty(val, lo, hi):
        """0 if within range; fractional penalty outside, capped at 1."""
        span = max(hi - lo, 1)
        if val < lo:
            return min((lo - val) / span, 1.0)
        elif val > hi:
            return min((val - hi) / span, 1.0)
        return 0.0

    t_pen = soft_penalty(temp,     t_min, t_max)
    h_pen = soft_penalty(humidity, h_min, h_max)
    r_pen = soft_penalty(rainfall, r_min, r_max)

    # Temperature weighted 2x; humidity and rainfall 1x each
    return 2 * t_pen + h_pen + r_pen


def check_day_suitability(crop, temp, humidity, rainfall):
    """
    Returns 'good' or 'bad' for a single forecast day.

    A day is considered BAD only when the temperature is significantly out of
    range (hard constraint) OR when BOTH humidity AND rainfall are out of range
    at the same time.  A single mild deviation does not doom the day.
    """
    cond = CROP_CONDITIONS.get(crop)
    if not cond:
        return 'bad'

    t_min, t_max = cond['temp']
    h_min, h_max = cond['humidity']
    r_min, r_max = cond['rainfall']

    # Allow a 15 % tolerance buffer on each boundary
    t_buf = max((t_max - t_min) * 0.15, 2.0)
    h_buf = max((h_max - h_min) * 0.15, 5.0)
    r_buf = max((r_max - r_min) * 0.15, 5.0)

    temp_ok     = (t_min - t_buf) <= temp     <= (t_max + t_buf)
    humidity_ok = (h_min - h_buf) <= humidity <= (h_max + h_buf)
    rainfall_ok = (r_min - r_buf) <= rainfall <= (r_max + r_buf)

    # Temperature out of range → always bad (hard constraint)
    if not temp_ok:
        return 'bad'

    # Both humidity AND rainfall out of range → bad
    if not humidity_ok and not rainfall_ok:
        return 'bad'

    return 'good'


def compute_analysis_status(good_days, total_days):
    """
    Returns (status_key, status_label_en, status_label_hi) based on
    the fraction of good days in the forecast window.
    """
    if total_days == 0:
        return 'warning', 'No Data', 'कोई डेटा नहीं'

    ratio = good_days / total_days

    if ratio >= 0.75:
        return 'excellent', 'Excellent Conditions', 'उत्कृष्ट स्थिति'
    elif ratio >= 0.50:
        return 'good', 'Good Conditions', 'अच्छी स्थिति'
    elif ratio >= 0.30:
        return 'warning', 'Moderate Risk', 'मध्यम जोखिम'
    else:
        return 'danger', 'High Risk', 'खतरनाक स्थिति'


def pick_best_from_rules(valid_crops, temp, humidity, rainfall):
    if not valid_crops:
        return None
    scored = sorted(valid_crops, key=lambda c: score_crop_against_weather(c, temp, humidity, rainfall))
    return scored[0]


def compute_irrigation_data(crop, rainfall, humidity, irrigation_possible=True):
    """
    Derives all irrigation-related variables.
    If irrigation_possible is False, returns irrigation_added = 0 and a
    'no irrigation' flag so the UI shows correct info.
    """
    cond = CROP_CONDITIONS.get(crop, {})
    rain_min = cond.get('rainfall', [50, 150])[0]
    rain_max = cond.get('rainfall', [50, 150])[1]
    crop_rain_need = (rain_min + rain_max) / 2

    total_rainfall_15d = round(rainfall * 0.5, 1)
    effective_rainfall = round(total_rainfall_15d * 0.8, 1)

    deficit = crop_rain_need - effective_rainfall

    if not irrigation_possible:
        irrigation_available = False
        irrigation_added = 0
        if deficit > 0:
            irr_freq = 0
            irr_label = "सिंचाई उपलब्ध नहीं — प्राकृतिक वर्षा पर निर्भर रहना होगा"
            irr_label_en = "No irrigation available — crop depends on natural rainfall"
        else:
            irr_freq = 0
            irr_label = "वर्षा पर्याप्त — सिंचाई की आवश्यकता नहीं"
            irr_label_en = "Rainfall sufficient — no irrigation needed"
    else:
        irrigation_added = max(0, round(deficit, 1))
        irrigation_available = irrigation_added > 0
        if irrigation_added == 0:
            irr_freq = 0
            irr_label = "वर्षा पर्याप्त — सिंचाई की आवश्यकता नहीं"
            irr_label_en = "Rainfall sufficient — no irrigation needed"
        elif irrigation_added < 20:
            irr_freq = 1
            irr_label = "हल्की पूरक सिंचाई की सिफारिश"
            irr_label_en = "Light supplemental irrigation recommended"
        elif irrigation_added < 50:
            irr_freq = 2
            irr_label = "मध्यम सिंचाई आवश्यक"
            irr_label_en = "Moderate irrigation required"
        elif irrigation_added < 90:
            irr_freq = 3
            irr_label = "नियमित सिंचाई आवश्यक"
            irr_label_en = "Regular irrigation required"
        else:
            irr_freq = 4
            irr_label = "भारी सिंचाई आवश्यक — फसल को अधिक पानी चाहिए"
            irr_label_en = "Heavy irrigation needed — crop needs significant water"

    return {
        "irrigation_available":  irrigation_available,
        "irrigation_added":      irrigation_added,
        "total_rainfall_15d":    total_rainfall_15d,
        "effective_rainfall":    effective_rainfall,
        "irr_freq":              irr_freq,
        "irr_label":             irr_label,
        "irr_label_en":          irr_label_en,
    }
