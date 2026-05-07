# ai_server.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

from deep_translator import GoogleTranslator

import os
import json
import re
import asyncio
from functools import lru_cache

# =========================================
# LOAD ENV
# =========================================

load_dotenv("backend/.env")

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

print(
    "OPENROUTER KEY:",
    OPENROUTER_API_KEY
)

# =========================================
# FASTAPI
# =========================================

app = FastAPI()

# =========================================
# CORS
# =========================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)

# =========================================
# OPENROUTER CLIENT
# =========================================

client = OpenAI(

    api_key=OPENROUTER_API_KEY,

    base_url=
    "https://openrouter.ai/api/v1"

)

# =========================================
# LABELS
# =========================================

CATEGORIES = [

    "sports",
    "politics",
    "technology",
    "business",
    "health",
    "entertainment",
    "general"

]

STATES = [

    "tamil nadu",
    "andhra pradesh",
    "karnataka",
    "kerala",
    "telangana",
    "india",
    "world"

]

# =========================================
# LANGUAGE MAP
# =========================================

LANGUAGE_MAP = {

    "en":"en",
    "te":"te",
    "ta":"ta",
    "kn":"kn",
    "hi":"hi",
    "ml":"ml"

}

# =========================================
# TRANSLATION CACHE
# =========================================

translation_cache = {}

# =========================================
# REQUEST MODELS
# =========================================

class NewsRequest(BaseModel):

    title:str = ""
    description:str = ""
    content:str = ""

class TranslateRequest(BaseModel):

    title:str = ""
    summary:str = ""
    source:str = ""
    state:str = ""
    category:str = ""
    target_lang:str = "en"

# =========================================
# CATEGORY KEYWORDS
# =========================================

CATEGORY_KEYWORDS = {

    "sports":[
        "cricket","ipl","football",
        "fifa","sports","match",
        "tournament","player",
        "stadium","odi","t20",
        "goal","tennis",
        "badminton","kabaddi"
    ],

    "politics":[
        "election","minister",
        "government","parliament",
        "assembly","mla","mp",
        "chief minister",
        "prime minister",
        "bjp","congress"
    ],

    "technology":[
        "ai","technology",
        "software","google",
        "microsoft","openai",
        "startup","robot",
        "cloud","chatgpt",
        "iphone","android"
    ],

    "business":[
        "market","stock",
        "business","finance",
        "economy","bank",
        "investment","profit",
        "revenue","sensex",
        "nifty"
    ],

    "health":[
        "hospital","doctor",
        "health","medical",
        "virus","covid",
        "vaccine","medicine",
        "patient"
    ],

    "entertainment":[
        "movie","actor",
        "cinema","music",
        "film","celebrity",
        "director","ott",
        "netflix","trailer"
    ]

}

# =========================================
# STATE KEYWORDS
# =========================================

STATE_KEYWORDS = {

    "tamil nadu":[
        "tamil nadu",
        "chennai",
        "coimbatore",
        "madurai",
        "trichy",
        "salem",
        "vellore"
    ],

    "andhra pradesh":[
        "andhra pradesh",
        "visakhapatnam",
        "vijayawada",
        "tirupati",
        "guntur"
    ],

    "telangana":[
        "telangana",
        "hyderabad",
        "warangal"
    ],

    "kerala":[
        "kerala",
        "kochi",
        "kozhikode"
    ],

    "karnataka":[
        "karnataka",
        "bengaluru",
        "mysore",
        "mangalore"
    ],

    "india":[
        "india",
        "indian",
        "delhi",
        "mumbai"
    ]

}

# =========================================
# CLEAN TEXT
# =========================================

def clean_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"http\S+",
        "",
        text
    )

    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()

# =========================================
# DETECT CATEGORY
# =========================================

@lru_cache(maxsize=1000)

def detect_category(text):

    text = clean_text(text)

    scores = {}

    for category,words in CATEGORY_KEYWORDS.items():

        scores[category] = 0

        for word in words:

            pattern = rf"\b{re.escape(word)}\b"

            matches = re.findall(
                pattern,
                text
            )

            scores[category] += len(matches)

    best_category = max(
        scores,
        key=scores.get
    )

    if scores[best_category] == 0:
        return "general"

    return best_category

# =========================================
# DETECT STATE
# =========================================

@lru_cache(maxsize=1000)

def detect_state(text):

    text = clean_text(text)

    scores = {}

    for state,words in STATE_KEYWORDS.items():

        scores[state] = 0

        for word in words:

            pattern = rf"\b{re.escape(word)}\b"

            matches = re.findall(
                pattern,
                text
            )

            scores[state] += len(matches)

    best_state = max(
        scores,
        key=scores.get
    )

    if scores[best_state] == 0:
        return "world"

    return best_state

# =========================================
# SUMMARY
# =========================================

def generate_summary(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if len(text) <= 180:
        return text

    return text[:180] + "..."

# =========================================
# AI CHECK
# =========================================

def needs_ai(category,state):

    if category == "general":
        return True

    if state == "world":
        return True

    return False

# =========================================
# CLASSIFY API
# =========================================

@app.post("/classify")
async def classify(data: NewsRequest):

    try:

        full_text = f"""
        {data.title}

        {data.description}

        {data.content}
        """

        rule_category = detect_category(
            full_text
        )

        rule_state = detect_state(
            full_text
        )

        summary = generate_summary(
            data.description
            or data.title
            or ""
        )

        if not needs_ai(
            rule_category,
            rule_state
        ):

            return {

                "category":
                rule_category,

                "state":
                rule_state,

                "summary":
                summary

            }

        prompt = f"""
Classify this Indian news.

Allowed categories:
{CATEGORIES}

Allowed states:
{STATES}

Return ONLY JSON.

FORMAT:
{{
 "category":"technology",
 "state":"tamil nadu",
 "summary":"short summary"
}}

NEWS:
{full_text}
"""

        try:

            response = await asyncio.to_thread(

                lambda:
                client.chat.completions.create(

                    model=
                    "openai/gpt-4.1-mini",

                    messages=[

                        {
                            "role":"system",
                            "content":
                            "You are an accurate Indian news classifier."
                        },

                        {
                            "role":"user",
                            "content":
                            prompt
                        }

                    ],

                    temperature=0.1,

                    max_tokens=80,

                    timeout=5

                )

            )

            content = (
                response
                .choices[0]
                .message.content
            )

            try:
                result = json.loads(content)
            except:
                result = {}

            category = result.get(
                "category",
                rule_category
            )

            state = result.get(
                "state",
                rule_state
            )

            ai_summary = result.get(
                "summary",
                summary
            )

            if category not in CATEGORIES:
                category = rule_category

            if state not in STATES:
                state = rule_state

            return {

                "category":
                category,

                "state":
                state,

                "summary":
                generate_summary(
                    ai_summary
                )

            }

        except Exception as ai_error:

            print(
                "AI FALLBACK ERROR:",
                ai_error
            )

            return {

                "category":
                rule_category,

                "state":
                rule_state,

                "summary":
                summary

            }

    except Exception as e:

        print(
            "CLASSIFY ERROR:",
            e
        )

        return {

            "category":
            "general",

            "state":
            "world",

            "summary":
            generate_summary(
                data.description
                or data.title
                or ""
            )

        }

# =========================================
# TRANSLATE API
# =========================================

@app.post("/translate")
async def translate(data: TranslateRequest):

    try:

        lang = LANGUAGE_MAP.get(
            data.target_lang,
            "en"
        )

        if lang == "en":

            return {

                "title":
                data.title,

                "summary":
                data.summary,

                "source":
                data.source,

                "state":
                data.state,

                "category":
                data.category

            }

        cache_key = f"""
        {data.title}
        {data.summary}
        {lang}
        """

        if cache_key in translation_cache:

            return translation_cache[
                cache_key
            ]

        translator = GoogleTranslator(
            source="auto",
            target=lang
        )

        def safe_translate(text):

            try:

                if not text:
                    return ""

                return translator.translate(
                    text
                )

            except:
                return text

        translated_data = {

            "title":
            safe_translate(
                data.title
            ),

            "summary":
            safe_translate(
                data.summary
            ),

            "source":
            safe_translate(
                data.source
            ),

            "state":
            safe_translate(
                data.state
            ),

            "category":
            safe_translate(
                data.category
            )

        }

        translation_cache[
            cache_key
        ] = translated_data

        return translated_data

    except Exception as e:

        print(
            "TRANSLATE ERROR:",
            e
        )

        return {

            "title":
            data.title,

            "summary":
            data.summary,

            "source":
            data.source,

            "state":
            data.state,

            "category":
            data.category

        }

# =========================================
# HOME
# =========================================

@app.get("/")
async def home():

    return {

        "message":
        "Optimized AI News Service Running"

    }