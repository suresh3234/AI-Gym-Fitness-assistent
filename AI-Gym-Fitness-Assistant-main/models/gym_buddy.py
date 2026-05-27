"""
models/gym_buddy.py – Virtual Gym Buddy Chatbot.

Provides conversational fitness guidance using either a local rule-based
engine or an LLM API (Gemini / OpenAI) if an API key is configured.
Includes sentiment-based response modulation.
"""
import os
import re
import random


# ---------------------------------------------------------------------------
# Sentiment helper (keyword-based, no heavy NLP dependency)
# ---------------------------------------------------------------------------

POSITIVE_WORDS = {"great", "good", "awesome", "happy", "motivated", "strong",
                  "excellent", "fantastic", "ready", "energetic", "excited"}
NEGATIVE_WORDS = {"tired", "lazy", "unmotivated", "sad", "stressed", "bad",
                  "weak", "exhausted", "depressed", "hurt", "sick", "pain"}


def simple_sentiment(text: str) -> str:
    """Return 'positive', 'negative', or 'neutral' for *text*."""
    words = set(re.findall(r"\b\w+\b", text.lower()))
    pos_hits = words & POSITIVE_WORDS
    neg_hits = words & NEGATIVE_WORDS
    if len(pos_hits) > len(neg_hits):
        return "positive"
    elif len(neg_hits) > len(pos_hits):
        return "negative"
    return "neutral"


# ---------------------------------------------------------------------------
# Rule-based response engine
# ---------------------------------------------------------------------------

RULES: list[tuple[str, list[str]]] = [
    # Pattern                          Responses
    (r"\bhi\b|\bhello\b|\bhey\b",
     ["Hey there! Ready to crush today's workout? 💪",
      "Hello! I'm your AI Gym Buddy. How can I help you today?",
      "Hi! Let's talk fitness!"]),

    (r"weight loss|lose weight|fat loss",
     ["Focus on a calorie deficit of 300-500 kcal/day combined with strength training.",
      "Cardio helps, but lifting weights boosts your metabolism long-term.",
      "Try HIIT – it burns more calories in less time than steady-state cardio."]),

    (r"muscle gain|bulk|build muscle",
     ["Aim for 1.6–2.2 g of protein per kg of bodyweight daily.",
      "Progressive overload is key – add weight or reps every week.",
      "Compound movements like squats, deadlifts, and bench press are your best friends."]),

    (r"diet|nutrition|eat|food|meal",
     ["Prioritise whole foods: lean proteins, complex carbs, and healthy fats.",
      "Don't skip breakfast – it jumpstarts your metabolism.",
      "Meal-prep on Sundays to stay on track during busy weekdays."]),

    (r"cardio|running|cycling|swim",
     ["Aim for 150 minutes of moderate cardio per week.",
      "Zone 2 cardio (conversational pace) is excellent for fat burning.",
      "Mix LISS and HIIT for the best cardiovascular adaptations."]),

    (r"rest|recovery|sleep",
     ["Muscles grow during rest, not during exercise. Sleep 7-9 hours.",
      "Take at least 1-2 rest days per week to prevent overtraining.",
      "Active recovery (light walk, yoga) can help sore muscles recover faster."]),

    (r"motivation|lazy|skip|don't feel",
     ["Remember why you started – your goals haven't changed.",
      "Even a 10-minute workout beats nothing. Start small!",
      "Put on your shoes, walk to the gym – often that's the hardest step."]),

    (r"injury|pain|hurt|sore",
     ["Listen to your body. Sharp pain = stop immediately and consult a doctor.",
      "RICE method for minor injuries: Rest, Ice, Compression, Elevation.",
      "Delayed onset muscle soreness (DOMS) is normal 24-48 hours after training."]),

    (r"supplement|protein powder|creatine",
     ["Creatine monohydrate is the most evidence-backed supplement for strength.",
      "Whey protein is convenient, but whole-food protein is just as effective.",
      "Supplements help, but they can't replace a solid diet."]),

    (r"beginner|start|new to",
     ["Start with 3 full-body workouts per week – consistency beats intensity.",
      "Learn the basics: squat, hinge, push, pull, carry.",
      "Don't try to do everything at once – master the fundamentals first."]),
]


class GymBuddy:
    """
    Conversational AI gym buddy.
    Falls back to rule-based responses when no LLM API key is set.
    """

    def __init__(self):
        self._api_key = os.getenv("LLM_API_KEY", "")
        self._use_llm = bool(self._api_key)
        self._history: list[dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, user_message: str) -> str:
        """
        Accept a user message and return the assistant's reply.
        Uses LLM if API key is set, otherwise falls back to rule-based engine.
        """
        sentiment = simple_sentiment(user_message)
        self._history.append({"role": "user", "content": user_message})

        if self._use_llm:
            reply = self._llm_reply(user_message, sentiment)
        else:
            reply = self._rule_reply(user_message, sentiment)

        self._history.append({"role": "assistant", "content": reply})
        return reply

    def clear_history(self):
        """Reset conversation history."""
        self._history.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rule_reply(self, message: str, sentiment: str) -> str:
        """Match message against rule patterns and return a reply."""
        lower = message.lower()
        for pattern, responses in RULES:
            if re.search(pattern, lower):
                reply = random.choice(responses)
                return self._add_sentiment_prefix(reply, sentiment)

        # Fallback
        fallbacks = [
            "That's a great question! Focus on consistency and trust the process.",
            "Every step counts. Keep showing up and results will follow.",
            "I'm here to help! Could you tell me more about your fitness goal?",
        ]
        return self._add_sentiment_prefix(random.choice(fallbacks), sentiment)

    def _add_sentiment_prefix(self, reply: str, sentiment: str) -> str:
        """Prepend a sentiment-aware opener to the reply."""
        if sentiment == "positive":
            prefix = random.choice(["Love the energy! ", "Great attitude! ", "You're crushing it! "])
        elif sentiment == "negative":
            prefix = random.choice(["I hear you. ", "That's tough – but you can do this. ",
                                     "Let's turn that around together. "])
        else:
            prefix = ""
        return prefix + reply

    def _llm_reply(self, message: str, sentiment: str) -> str:
        """
        Call an LLM API (Gemini / OpenAI compatible) to generate a reply.
        Falls back to rule engine on error.
        """
        try:
            import httpx

            # Build a minimal system prompt
            system = (
                "You are an expert AI gym and fitness assistant. "
                "Give concise, evidence-based advice. "
                "Be encouraging and supportive. "
                "Keep responses under 100 words."
            )
            messages = [{"role": "system", "content": system}] + self._history[-6:]

            # Try OpenAI-compatible endpoint
            url = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
            model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
            headers = {"Authorization": f"Bearer {self._api_key}",
                       "Content-Type": "application/json"}
            payload = {"model": model, "messages": messages, "max_tokens": 150}

            resp = httpx.post(url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            return self._add_sentiment_prefix(content, sentiment)

        except Exception:
            return self._rule_reply(message, sentiment)
