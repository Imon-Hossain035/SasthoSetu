"""Deterministic Rule-Based Safety-Net Engine for SasthoSetu (Prompt 10).

This module implements the primary safety layer for SasthoSetu:
- Detects predefined acute emergency red flags across English, Bangla, and Banglish.
- Operates 100% offline with zero external dependencies.
- Completely deterministic: the same input will always produce the identical safety-net result.
- Strictly provides triage urgency prioritization (URGENT), NOT medical diagnosis or disease labeling.
"""

from typing import Any, Dict, List, Optional, Tuple


def normalize_symptoms(text: str) -> str:
    """Normalizes symptom descriptions for consistent pattern matching.

    - Converts Latin characters to lowercase.
    - Strips leading and trailing whitespace.
    - Normalizes punctuation and symbols to spaces (including Bengali dori '।').
    - Collapses consecutive whitespace characters.
    """
    if not text:
        return ""

    normalized = text.lower()
    # Strip common punctuation that could attach to words or disrupt phrase matching
    punctuation_to_space = [
        ",", ".", "!", "?", ";", ":", "(", ")", "[", "]",
        "{", "}", "\"", "'", "`", "/", "\\", "-", "_", "+",
        "=", "@", "#", "$", "%", "^", "&", "*", "~", "|",
        "\n", "\r", "\t", "।", "—", "–"
    ]
    for char in punctuation_to_space:
        normalized = normalized.replace(char, " ")

    # Collapse repeated whitespace
    return " ".join(normalized.split())


# =============================================================================
# Emergency Red-Flag Rule Definitions
# =============================================================================
# Structured rule categories covering high-risk presentations described in the
# SasthoSetu project framework. Each entry includes:
#   - id: Unique rule identifier
#   - category: Clinician-facing category title
#   - description: Conservative, non-diagnostic explanation of why the rule fired
#   - patterns: Direct phrases in English, Bangla, and Banglish
#   - token_pairs: (Primary words, Secondary modifier words) to catch natural phrasing
# =============================================================================

SAFETY_RULES: List[Dict[str, Any]] = [
    {
        "id": "chest_pain",
        "category": "Severe Chest Pain / Cardiovascular Red Flag",
        "description": "Severe chest pain, crushing discomfort, or chest pressure was reported.",
        "patterns": [
            # English
            "chest pain", "pain in chest", "chest pressure", "tightness in chest",
            "crushing chest pain", "heavy chest pain", "heart pain", "heart attack",
            "pain radiating to left arm", "chest heaviness",
            # Bangla
            "বুকে ব্যথা", "বুকে ব্যাথা", "বুক ব্যথা", "বুক ব্যাথা",
            "বুকে প্রচণ্ড ব্যথা", "বুকে তীব্র ব্যথা", "বুকে তীব্র ব্যাথা",
            "বুকে চাপ", "বুকে ভার", "বুক ধড়ফড়", "বুক চেপে আসছে",
            # Banglish
            "buk betha", "buke betha", "buk byatha", "buke byatha",
            "buke chap", "buke bhor", "buke prochondo betha", "buke tibro betha",
            "buker betha", "buke khub betha", "buk chap"
        ],
        "token_pairs": (
            ["chest", "বুক", "বুকে", "buk", "buke", "buker"],
            ["pain", "pressure", "tightness", "crushing", "heaviness", "ব্যথা", "ব্যাথা", "চাপ", "ভার", "betha", "byatha", "chap"]
        ),
    },
    {
        "id": "respiratory_distress",
        "category": "Severe Difficulty Breathing / Respiratory Distress",
        "description": "Severe breathing difficulty or respiratory distress was reported.",
        "patterns": [
            # English
            "difficulty breathing", "trouble breathing", "shortness of breath",
            "severe breathlessness", "cant breathe", "cannot breathe",
            "gasping for air", "respiratory distress", "choking", "turning blue",
            "struggling to breathe", "severe asthma attack",
            # Bangla
            "শ্বাস নিতে কষ্ট", "শ্বাসকষ্ট", "শ্বাস কষ্ট", "নিশ্বাস নিতে কষ্ট",
            "নিঃশ্বাস নিতে কষ্ট", "দম বন্ধ হয়ে আসছে", "দম নিতে পারছি না",
            "শ্বাসরোধ", "শ্বাস আটকে আসছে", "হাঁপিয়ে উঠছে", "শ্বাস নিতে পারছি না",
            # Banglish
            "shash nite kosto", "shashkosto", "shas kosto", "shash nite koshto",
            "dom bondho", "dom nite parsi na", "nisshash nite kosto",
            "shash nite khub kosto", "shas nite kosto", "shash nite parchi na"
        ],
        "token_pairs": (
            ["breath", "breathing", "respiratory", "শ্বাস", "নিশ্বাস", "নিঃশ্বাস", "দম", "shash", "shas", "nisshash", "dom"],
            ["difficulty", "distress", "shortness", "choking", "struggling", "কষ্ট", "বন্ধ", "আটকে", "রোধ", "kosto", "koshto", "bondho", "atke"]
        ),
    },
    {
        "id": "severe_bleeding",
        "category": "Severe or Uncontrolled Bleeding",
        "description": "Severe, heavy, or uncontrolled bleeding was reported.",
        "patterns": [
            # English
            "severe bleeding", "uncontrolled bleeding", "bleeding profusely",
            "heavy bleeding", "bleeding will not stop", "bleeding wont stop",
            "bleeding is severe", "coughing blood", "vomiting blood",
            "blood in vomit", "blood in sputum", "hemorrhage", "haemorrhage",
            # Bangla
            "রক্ত পড়া বন্ধ হচ্ছে না", "রক্ত পড়া থামছে না", "রক্তপাত",
            "প্রচণ্ড রক্তপাত", "তীব্র রক্তপাত", "রক্ত বমি", "কাশির সাথে রক্ত",
            "অতিরিক্ত রক্তক্ষরণ", "রক্তক্ষরণ", "রক্ত পড়ছে বন্ধ হচ্ছে না",
            # Banglish
            "rokto pora bondho hocche na", "rokto pora bondho hochhe na",
            "rokto thamche na", "prochondo rokto", "onek rokto",
            "rokto bomi", "kashir sathe rokto", "rokto khoron",
            "rokto porche bondho", "bleeding bondho hocche na"
        ],
        "token_pairs": (
            ["bleeding", "hemorrhage", "haemorrhage", "রক্ত", "রক্তপাত", "রক্তক্ষরণ", "rokto"],
            ["severe", "uncontrolled", "stop", "wont", "profuse", "heavy", "vomit", "cough", "বন্ধ", "থামছে", "বমি", "কাশি", "bondho", "thamche", "bomi", "kashi"]
        ),
    },
    {
        "id": "loss_of_consciousness",
        "category": "Loss of Consciousness / Unresponsiveness",
        "description": "Loss of consciousness, fainting, or unresponsiveness was reported.",
        "patterns": [
            # English
            "unconscious", "became unconscious", "loss of consciousness",
            "passed out", "fainted", "unresponsive", "collapsed",
            "blacked out", "not waking up", "lost consciousness", "coma",
            # Bangla
            "অজ্ঞান", "অচেতন", "জ্ঞান হারিয়ে", "জ্ঞান হারিয়ে ফেলা",
            "জ্ঞান হারানো", "বেহুঁশ", "সাড়াহীন", "চেতনাহীন",
            "চোখ খুলছে না", "ডাকলে সাড়া দেয় না",
            # Banglish
            "oggan", "oggyan", "gyan hariye fela", "gyan hariye",
            "gyan harano", "behush", "sharahin", "sarahin",
            "chokh khulche na", "dakle shara dey na"
        ],
        "token_pairs": None,
    },
    {
        "id": "stroke_signs",
        "category": "Suspected Acute Stroke Signs",
        "description": "Potential acute stroke indicators (facial drooping, slurred speech, or sudden paralysis) were reported.",
        "patterns": [
            # English
            "stroke", "facial drooping", "face drooping", "slurred speech",
            "sudden paralysis", "sudden weakness", "one side paralyzed",
            "mouth crooked", "loss of speech", "hemiplegia", "unable to speak",
            # Bangla
            "স্ট্রোক", "মুখ বেঁকে যাওয়া", "মুখ বাঁকা", "কথা জড়িয়ে যাওয়া",
            "কথা বলতে পারছে না", "শরীরের এক পাশ অবশ", "একপাশ অবশ",
            "একপাশ প্যারালাইজড", "হাত পা অবশ হয়ে গেছে",
            # Banglish
            "stroke", "mukh beke gese", "mukh baka", "kotha joriye jacche",
            "kotha bolte parche na", "ek pas obosh", "ek side obosh",
            "paralyzed", "ek side obosh hoye gese"
        ],
        "token_pairs": None,
    },
    {
        "id": "severe_trauma",
        "category": "Severe Trauma / Head Injury",
        "description": "Severe trauma, major accident, or head injury was reported.",
        "patterns": [
            # English
            "head injury", "severe trauma", "major accident", "road accident",
            "compound fracture", "hit on head", "severe head trauma",
            "skull fracture", "deep wound bleeding heavily",
            # Bangla
            "মাথায় গুরুতর আঘাত", "মাথায় আঘাত", "মারাত্মক দুর্ঘটনা",
            "সড়ক দুর্ঘটনা", "গভীর ক্ষত", "হাড় ভেঙে গেছে", "মাথা ফেটে গেছে",
            # Banglish
            "mathay aghat", "bipojjonok durghotona", "shorok durghotona",
            "har venge gese", "accident e gurutoro aghat", "matha fete gese"
        ],
        "token_pairs": None,
    },
    {
        "id": "seizure",
        "category": "Seizure / Convulsions",
        "description": "Seizure or acute convulsions were reported.",
        "patterns": [
            # English
            "seizure", "seizures", "having a seizure", "convulsion",
            "convulsions", "fits", "epileptic fit", "epilepsy attack",
            # Bangla
            "খিঁচুনি", "তীব্র খিঁচুনি", "ফিট হয়ে যাওয়া", "মৃগী",
            "মৃগীর খিঁচুনি", "চোখ উল্টে যাওয়া",
            # Banglish
            "khichuni", "khicuni", "fit hoye jawa", "fit hoye geche",
            "chokh ulte gese", "chokh ulte jawa"
        ],
        "token_pairs": None,
    },
    {
        "id": "severe_allergic_reaction",
        "category": "Severe Allergic Reaction / Anaphylaxis",
        "description": "Signs suggestive of severe allergic reaction or airway compromise were reported.",
        "patterns": [
            # English
            "anaphylaxis", "severe allergic reaction", "swollen throat",
            "throat closing", "severe allergy", "swelling of tongue",
            # Bangla
            "অ্যালার্জিজনিত শ্বাসকষ্ট", "গলা ফুলে যাওয়া", "তীব্র অ্যালার্জি",
            "শ্বাস নালী ফুলে যাওয়া", "মুখ ফুলে শ্বাসকষ্ট",
            # Banglish
            "anaphylaxis", "gola fule gese", "tibro allergy",
            "shash nali fule gese", "severe allergy"
        ],
        "token_pairs": None,
    },
    {
        "id": "severe_burns",
        "category": "Severe Burns",
        "description": "Severe or extensive thermal or chemical burns were reported.",
        "patterns": [
            # English
            "severe burn", "severe burns", "body burned", "acid burn",
            "extensive burns", "deep burn", "third degree burn",
            # Bangla
            "তীব্র পোড়া", "আগুনে পোড়া", "গভীর পোড়া", "অ্যাসিডে পোড়া",
            "শরীরের বড় অংশ পুড়ে গেছে",
            # Banglish
            "severe burn", "pure gese", "prochondo pora", "tibro pora",
            "acid a pora"
        ],
        "token_pairs": None,
    },
    {
        "id": "poisoning_overdose",
        "category": "Poisoning / Toxic Ingestion / Overdose",
        "description": "Acute toxic ingestion, pesticide exposure, or medication overdose was reported.",
        "patterns": [
            # English
            "poisoning", "drank poison", "ingested poison", "swallowed poison",
            "pesticide poisoning", "overdose", "chemical ingestion", "drank pesticide",
            "swallowed pesticide", "ingested pesticide",
            # Bangla
            "বিষ খেয়েছে", "বিষ খেয়েছে", "বিষ পান", "কীটনাশক পান", "বিষাক্ত কিছু খেয়েছে",
            "বিষাক্ত কিছু খেয়েছে", "ওষুধের ওভারডোজ", "বিষক্রিয়া", "বিষক্রিয়া",
            # Banglish
            "bish kheyeche", "bish pan", "kitnashok pan", "overdose",
            "bishkriya", "poisoning"
        ],
        "token_pairs": (
            ["poison", "poisoning", "toxic", "pesticide", "বিষ", "কীটনাশক", "bish", "kitnashok"],
            ["swallowed", "drank", "ingested", "taken", "overdose", "chemical", "খেয়েছে", "খেয়েছে", "পান", "kheyeche", "pan"]
        ),
    },
]

# Standard safety-net immediate clinical guidance advice (non-diagnostic)
SAFETY_NET_URGENT_ADVICE = (
    "A potential emergency warning sign was detected. "
    "Seek immediate medical attention and do not delay care while waiting for an automated assessment."
)

RULE_FRIENDLY_NAMES: Dict[str, str] = {
    "chest_pain": "Severe Chest Pain / Chest Discomfort",
    "respiratory_distress": "Difficulty Breathing / Respiratory Distress",
    "severe_bleeding": "Severe or Uncontrolled Bleeding",
    "loss_of_consciousness": "Loss of Consciousness / Unresponsiveness",
    "stroke_signs": "Suspected Acute Stroke Warning Signs",
    "severe_trauma": "Severe Trauma / Head Injury",
    "seizure": "Acute Seizure / Convulsions",
    "severe_allergic_reaction": "Severe Allergic Reaction / Airway Swelling",
    "severe_burns": "Severe Thermal or Chemical Burns",
    "poisoning_overdose": "Poisoning / Toxic Exposure / Overdose",
}


def get_rule_readable_label(rule_id: str) -> str:
    """Returns a clean, user-facing label for a matched rule ID without exposing internal variables."""
    return RULE_FRIENDLY_NAMES.get(rule_id, rule_id.replace("_", " ").title())


def _pattern_matches(pattern: str, text: str) -> bool:
    """Checks whether a normalized pattern exists cleanly in normalized text.

    Uses space padding to ensure boundary separation for both Latin and Bengali phrases,
    preventing sub-word accidental triggers.
    """
    padded_pattern = f" {pattern} "
    padded_text = f" {text} "
    return padded_pattern in padded_text


def _tokens_co_occur(primary_tokens: List[str], secondary_tokens: List[str], text: str) -> bool:
    """Checks if any primary concept word and any secondary modifier word co-occur in the text.

    Ensures high sensitivity for natural human language variants while guarding against false positives.
    """
    words_in_text = set(text.split())
    has_primary = any(p in words_in_text or f" {p} " in f" {text} " for p in primary_tokens)
    if not has_primary:
        return False
    return any(s in words_in_text or f" {s} " in f" {text} " for s in secondary_tokens)


def check_safety_rules(text: str) -> Dict[str, Any]:
    """Evaluates symptom text against the deterministic safety-net red-flag rules.

    Returns:
        Structured result dict:
        {
            "matched": bool,
            "urgency": "URGENT" or None,
            "matched_rules": List[Dict],
            "matched_rule_ids": List[str],
            "reason": str or None,
            "advice": str or None,
        }
    """
    normalized = normalize_symptoms(text)
    if not normalized:
        return {
            "matched": False,
            "urgency": None,
            "matched_rules": [],
            "matched_rule_ids": [],
            "reason": None,
            "advice": None,
        }

    matched_rules: List[Dict[str, Any]] = []
    matched_rule_ids: List[str] = []

    for rule in SAFETY_RULES:
        rule_matched = False
        matched_trigger = ""

        # 1. Check exact phrase patterns
        for pattern in rule["patterns"]:
            normalized_pattern = normalize_symptoms(pattern)
            if _pattern_matches(normalized_pattern, normalized):
                rule_matched = True
                matched_trigger = pattern
                break

        # 2. Check token co-occurrence if not already matched
        if not rule_matched and rule.get("token_pairs"):
            primary, secondary = rule["token_pairs"]
            if _tokens_co_occur(primary, secondary, normalized):
                rule_matched = True
                matched_trigger = f"{primary[0]} + {secondary[0]}"

        if rule_matched:
            matched_rule_ids.append(rule["id"])
            matched_rules.append(
                {
                    "rule_id": rule["id"],
                    "category": rule["category"],
                    "description": rule["description"],
                    "matched_pattern": matched_trigger,
                }
            )

    if matched_rules:
        # Build concise non-diagnostic reason
        categories_desc = ", ".join(r["category"].lower() for r in matched_rules)
        reason = f"Emergency warning sign detected: {categories_desc} was reported."

        return {
            "matched": True,
            "urgency": "URGENT",
            "matched_rules": matched_rules,
            "matched_rule_ids": matched_rule_ids,
            "reason": reason,
            "advice": SAFETY_NET_URGENT_ADVICE,
        }

    return {
        "matched": False,
        "urgency": None,
        "matched_rules": [],
        "matched_rule_ids": [],
        "reason": None,
        "advice": None,
    }
