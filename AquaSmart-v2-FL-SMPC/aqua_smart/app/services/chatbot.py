"""
Domain-trained rule-based chatbot for fish farming / aquaculture.
No external API. Intent detection via keyword matching + response templates.
"""
import re
from typing import Tuple


KNOWLEDGE_BASE = {
    "optimal_temperature": {
        "range": "22-26°C (ideal), 20-28°C (acceptable)",
        "effect": "Below 18°C fish become lethargic and stop eating. Above 30°C oxygen levels drop and stress increases.",
        "action": "Use shading, aeration, or water exchange to regulate temperature.",
    },
    "dissolved_oxygen": {
        "range": "≥ 5 mg/L (minimum), 6-8 mg/L (ideal)",
        "effect": "Low DO causes fish to surface, reduces growth rate, and can cause mass mortality below 2 mg/L.",
        "action": "Install aerators, reduce feeding, and increase water exchange when DO drops below 5 mg/L.",
    },
    "ph": {
        "range": "6.5-8.5 (acceptable), 7.0-8.0 (ideal)",
        "effect": "pH < 6.5 causes acidosis; pH > 9.0 causes alkalosis. Both impair gill function.",
        "action": "Add agricultural lime to raise pH; dilute with fresh water or add CO₂ to lower it.",
    },
    "turbidity": {
        "range": "10-30 NTU (acceptable)",
        "effect": "High turbidity reduces photosynthesis, light penetration, and oxygen production by algae.",
        "action": "Avoid overfeeding, manage runoff, and use flocculants if very high.",
    },
    "ammonia": {
        "range": "< 0.02 mg/L (safe), 0-0.01 mg/L (ideal)",
        "effect": "Ammonia is toxic even at low concentrations. Above 0.06 mg/L causes mass mortality.",
        "action": "Reduce feeding, increase aeration, perform partial water change (20-30%), check biofilter.",
    },
    "nitrate": {
        "range": "< 10 mg/L (acceptable)",
        "effect": "High nitrate indicates poor water turnover. Chronic exposure reduces immune function.",
        "action": "Perform partial water exchange weekly; plant aquatic vegetation as a biofilter.",
    },
    "feeding_frequency": {
        "info": "Feed 2-4 times daily. Juveniles need more frequent feeding (4-6×/day), adults 2×/day.",
        "timing": "Morning (6-9 AM) and evening (5-8 PM) are optimal feeding windows for most species.",
    },
    "feeding_rate": {
        "info": "Standard feeding rate: 3-5% of body biomass per day.",
        "formula": "Daily feed (kg) = Total fish biomass (kg) × feeding_rate / 100",
        "adjustment": "Reduce by 30-50% when water quality is suboptimal. Stop feeding in critical conditions.",
    },
    "fcr": {
        "info": "Feed Conversion Ratio (FCR) = Feed fed (kg) / Weight gained (kg). Lower is better.",
        "ideal": "FCR of 1.5-2.0 is good for tilapia; < 1.5 is excellent.",
        "improvement": "Improve FCR by optimising feed quality, water quality, and stocking density.",
    },
    "wqi": {
        "info": "Water Quality Index (WQI) is a composite score (0-100) combining temperature, DO, and pH.",
        "categories": "Excellent (80-100), Good (60-80), Fair (40-60), Poor (0-40)",
        "action": "Aim to keep WQI above 60 at all times for healthy fish growth.",
    },
    "stocking_density": {
        "info": "Recommended stocking density: 20-50 fish/m³ for intensive systems, 5-15 fish/m³ for semi-intensive.",
        "effect": "Overcrowding leads to oxygen depletion, stress, disease, and poor growth.",
    },
    "disease_prevention": {
        "info": "Most fish diseases are caused by poor water quality. Maintain optimal parameters to prevent outbreaks.",
        "signs": "Watch for loss of appetite, abnormal swimming, fin rot, white spots, or gasping at the surface.",
        "action": "Isolate sick fish, improve water quality, consult an aquaculture veterinarian.",
    },
}

INTENTS = [
    ("temperature",     r"temp(erature)?|°c|hot|cold|warm|heat|thermal"),
    ("dissolved_oxygen",r"(dissolved\s*)?oxygen|do\b|o2|aerat|suffocate|suffocation"),
    ("ph",              r"\bph\b|acid(ic)?|alkalin|basic|lime"),
    ("turbidity",       r"turbid|murky|cloudy|clear|ntu|visibility"),
    ("ammonia",         r"ammonia|nh3|nh4|toxic|poison"),
    ("nitrate",         r"nitrate|nitrite|no3|nitrogen"),
    ("feeding_rate",    r"how much (to )?feed|feed(ing)? (amount|rate|quantity)|kg|gram|daily feed"),
    ("feeding_frequency", r"how (often|many times|frequent)|times (per|a) day|when to feed|schedule"),
    ("fcr",             r"fcr|feed conversion|efficiency|ratio"),
    ("wqi",             r"wqi|water quality index|score|index"),
    ("stocking_density",r"stocking|density|overcrowd|fish per|m3|cubic"),
    ("disease_prevention", r"disease|sick|ill(ness)?|infection|symptom|parasite|bacteria|fin rot"),
    ("recommendation",  r"recommend|suggest|advice|what should|how to improve|best practice"),
    ("greeting",        r"hello|hi\b|hey|good (morning|afternoon|evening)|howdy|bonjour|salut"),
    ("help",            r"help|what can you|what do you|capabilities|feature|use|guide"),
    ("thanks",          r"thank(s| you)|merci|appreciate|great|awesome|perfect|good job"),
    ("model",           r"model|ml|machine learn|ai|predict|algorithm|accuracy|rmse|r2"),
]


def detect_intent(text: str) -> str:
    text_lower = text.lower()
    for intent, pattern in INTENTS:
        if re.search(pattern, text_lower):
            return intent
    return "general"


RESPONSES = {
    "greeting": {
        "reply": (
            "Hello! I'm **AquaBot**, your intelligent fish farming assistant. "
            "I can help you with water quality parameters, feeding recommendations, "
            "disease prevention, and more. What would you like to know?"
        ),
        "suggestions": ["What is the optimal temperature?", "How much should I feed my fish?", "What is WQI?"],
    },
    "help": {
        "reply": (
            "I can help you with:\n"
            "- **Water quality** - temperature, DO, pH, turbidity, ammonia, nitrate\n"
            "- **Feeding** - how much, how often, feeding schedules\n"
            "- **Feed Conversion Ratio (FCR)** - measuring and improving efficiency\n"
            "- **Disease prevention** - signs, causes, and treatments\n"
            "- **Stocking density** recommendations\n"
            "- **Water Quality Index (WQI)** interpretation\n\n"
            "Try asking something like *'What do I do when ammonia is high?'*"
        ),
        "suggestions": ["What is optimal pH?", "How often should I feed?", "Signs of fish disease"],
    },
    "thanks": {
        "reply": "You're welcome! Feel free to ask any time. Healthy fish, healthy farm!",
        "suggestions": ["Feeding schedule tips", "How to improve FCR", "Water change frequency"],
    },
    "temperature": {
        "reply": (
            "**Temperature Management**\n\n"
            f"- Optimal: {KNOWLEDGE_BASE['optimal_temperature']['range']}\n"
            f"- Effect: {KNOWLEDGE_BASE['optimal_temperature']['effect']}\n"
            f"- Action: {KNOWLEDGE_BASE['optimal_temperature']['action']}\n\n"
            "The AquaSmart system will recommend **STOP feeding** below 12°C or above 35°C, "
            "and **REDUCE feeding** outside the 20-28°C range."
        ),
        "suggestions": ["How does temperature affect feeding?", "What to do if water is too hot?", "Optimal DO levels"],
    },
    "dissolved_oxygen": {
        "reply": (
            "**Dissolved Oxygen (DO)**\n\n"
            f"- Target: {KNOWLEDGE_BASE['dissolved_oxygen']['range']}\n"
            f"- Effect: {KNOWLEDGE_BASE['dissolved_oxygen']['effect']}\n"
            f"- Action: {KNOWLEDGE_BASE['dissolved_oxygen']['action']}\n\n"
            "DO drops sharply at high temperatures and at night (algae consume O₂). "
            "Always monitor DO at dawn when levels are lowest."
        ),
        "suggestions": ["How to increase dissolved oxygen?", "Why does DO drop at night?", "Critical DO threshold"],
    },
    "ph": {
        "reply": (
            "**pH Management**\n\n"
            f"- Range: {KNOWLEDGE_BASE['ph']['range']}\n"
            f"- Effect: {KNOWLEDGE_BASE['ph']['effect']}\n"
            f"- Action: {KNOWLEDGE_BASE['ph']['action']}\n\n"
            "pH naturally fluctuates during the day - it rises in the afternoon (photosynthesis) "
            "and drops at night (respiration). Monitor twice daily."
        ),
        "suggestions": ["How to raise pH?", "How to lower pH?", "Does pH affect ammonia?"],
    },
    "turbidity": {
        "reply": (
            "**Turbidity**\n\n"
            f"- Range: {KNOWLEDGE_BASE['turbidity']['range']}\n"
            f"- Effect: {KNOWLEDGE_BASE['turbidity']['effect']}\n"
            f"- Action: {KNOWLEDGE_BASE['turbidity']['action']}\n\n"
            "Some turbidity from phytoplankton (green tint) is beneficial. "
            "Brown/grey turbidity from sediment or clay is harmful."
        ),
        "suggestions": ["How to reduce turbidity?", "Is green water good?", "Turbidity and oxygen"],
    },
    "ammonia": {
        "reply": (
            "**Ammonia Control**\n\n"
            f"- Safe level: {KNOWLEDGE_BASE['ammonia']['range']}\n"
            f"- Effect: {KNOWLEDGE_BASE['ammonia']['effect']}\n"
            f"- Action: {KNOWLEDGE_BASE['ammonia']['action']}\n\n"
            "Toxic ammonia (NH₃) increases at high pH and temperature. "
            "Total ammonia nitrogen (TAN) measurement should account for pH correction."
        ),
        "suggestions": ["Why is ammonia rising?", "Water change protocol", "Biofilter maintenance"],
    },
    "nitrate": {
        "reply": (
            "**Nitrate Management**\n\n"
            f"- Safe level: {KNOWLEDGE_BASE['nitrate']['range']}\n"
            f"- Effect: {KNOWLEDGE_BASE['nitrate']['effect']}\n"
            f"- Action: {KNOWLEDGE_BASE['nitrate']['action']}\n\n"
            "In the nitrogen cycle: ammonia → nitrite → nitrate. High nitrate means "
            "the biofilter is working but water exchange is insufficient."
        ),
        "suggestions": ["Nitrogen cycle in aquaculture", "How often to change water?", "Biofilter setup"],
    },
    "feeding_rate": {
        "reply": (
            "**Feeding Rate Guidelines**\n\n"
            f"- {KNOWLEDGE_BASE['feeding_rate']['info']}\n"
            f"- Formula: {KNOWLEDGE_BASE['feeding_rate']['formula']}\n"
            f"- Adjustment: {KNOWLEDGE_BASE['feeding_rate']['adjustment']}\n\n"
            "The AquaSmart ML model predicts the optimal feed amount per fish per day "
            "based on water quality and fish weight. Use the **Prediction** page for a real-time recommendation."
        ),
        "suggestions": ["What is FCR?", "When to reduce feeding?", "Optimal feeding schedule"],
    },
    "feeding_frequency": {
        "reply": (
            "**Feeding Schedule**\n\n"
            f"- {KNOWLEDGE_BASE['feeding_frequency']['info']}\n"
            f"- Best times: {KNOWLEDGE_BASE['feeding_frequency']['timing']}\n\n"
            "Overfeeding is the most common mistake - uneaten feed decomposes and "
            "raises ammonia. Feed only what fish consume in 5-10 minutes."
        ),
        "suggestions": ["Best time to feed fish", "How to avoid overfeeding?", "Feeding juveniles vs adults"],
    },
    "fcr": {
        "reply": (
            "**Feed Conversion Ratio (FCR)**\n\n"
            f"- {KNOWLEDGE_BASE['fcr']['info']}\n"
            f"- Target: {KNOWLEDGE_BASE['fcr']['ideal']}\n"
            f"- How to improve: {KNOWLEDGE_BASE['fcr']['improvement']}\n\n"
            "Track FCR weekly by recording total feed given and fish weight gains. "
            "A rising FCR signals suboptimal conditions or feed quality."
        ),
        "suggestions": ["How to calculate FCR?", "Ideal FCR by species", "Improve feed efficiency"],
    },
    "wqi": {
        "reply": (
            "**Water Quality Index (WQI)**\n\n"
            f"- {KNOWLEDGE_BASE['wqi']['info']}\n"
            f"- Categories: {KNOWLEDGE_BASE['wqi']['categories']}\n"
            f"- Goal: {KNOWLEDGE_BASE['wqi']['action']}\n\n"
            "WQI is calculated from temperature, dissolved oxygen, and pH scores. "
            "The dashboard displays your real-time WQI as a gauge."
        ),
        "suggestions": ["How is WQI calculated?", "WQI and feeding strategy", "Improve WQI score"],
    },
    "stocking_density": {
        "reply": (
            "**Stocking Density**\n\n"
            f"- {KNOWLEDGE_BASE['stocking_density']['info']}\n"
            f"- Risk: {KNOWLEDGE_BASE['stocking_density']['effect']}\n\n"
            "High stocking density requires strong aeration, biofiltration, and "
            "frequent feeding monitoring. Reduce density if DO consistently drops below 5 mg/L."
        ),
        "suggestions": ["Maximum fish per m³?", "Effects of overcrowding", "Tank vs pond density"],
    },
    "disease_prevention": {
        "reply": (
            "**Disease Prevention**\n\n"
            f"- {KNOWLEDGE_BASE['disease_prevention']['info']}\n"
            f"- Warning signs: {KNOWLEDGE_BASE['disease_prevention']['signs']}\n"
            f"- Action: {KNOWLEDGE_BASE['disease_prevention']['action']}\n\n"
            "Prevention is far more effective than treatment. Maintain WQI > 60 "
            "and follow a consistent feeding and monitoring schedule."
        ),
        "suggestions": ["Common fish diseases", "Quarantine protocol", "Water change schedule"],
    },
    "recommendation": {
        "reply": (
            "**Best Practices for Intelligent Fish Feeding**\n\n"
            "1. **Monitor daily** - Check temperature, DO, pH at dawn and dusk\n"
            "2. **Use the Prediction page** - Enter your readings for an ML-powered recommendation\n"
            "3. **Never overfeed** - Uneaten feed rots and pollutes the water\n"
            "4. **Act on alerts** - Red alerts require immediate action\n"
            "5. **Track FCR** - Weekly weight monitoring improves profitability\n"
            "6. **Maintain the biofilter** - Healthy bacteria break down ammonia\n"
            "7. **Log everything** - The Analytics page tracks trends over time"
        ),
        "suggestions": ["What is the feeding formula?", "How to use the prediction tool?", "WQI categories"],
    },
    "model": {
        "reply": (
            "**About the AquaSmart ML Model**\n\n"
            "The system uses a **Gradient Boosting Regressor** trained on IoT sensor data "
            "from multiple fish ponds. Key features include:\n\n"
            "- Water quality parameters (temp, DO, pH, turbidity, ammonia, nitrate)\n"
            "- Engineered features: Water Quality Index, thermal stress, DO deficit\n"
            "- Fish weight and interaction features\n\n"
            "The model predicts the **optimal feed amount (grams/fish/day)**. "
            "Run `scripts/train_model.py` with your own dataset for production accuracy."
        ),
        "suggestions": ["How accurate is the model?", "What features are used?", "Can I retrain the model?"],
    },
    "general": {
        "reply": (
            "I'm not sure I understood that. Could you rephrase? I can help with:\n"
            "- Water quality parameters (temperature, DO, pH, turbidity, ammonia)\n"
            "- Feeding rates, schedules, and strategies\n"
            "- Disease prevention and WQI interpretation\n\n"
            "Try asking something like *'What is the optimal pH for fish?'*"
        ),
        "suggestions": ["What is optimal temperature?", "How much feed per day?", "What is WQI?"],
    },
}


def get_response(message: str) -> dict:
    intent = detect_intent(message)
    resp = RESPONSES.get(intent, RESPONSES["general"])
    return {
        "reply": resp["reply"],
        "intent": intent,
        "suggestions": resp["suggestions"],
    }
