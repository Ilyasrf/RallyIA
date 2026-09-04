import logging
import os
import threading

from transformers import pipeline

logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("CHAT_MODEL_NAME", "Qwen/Qwen2.5-0.5B-Instruct")
MAX_TOKENS = int(os.getenv("CHAT_MAX_TOKENS", "250"))
generator = None
_load_lock = threading.Lock()


def _load_model():
    global generator
    if generator is not None:
        return

    with _load_lock:
        if generator is not None:
            return

        try:
            generator = pipeline(
                "text-generation",
                model=MODEL_NAME,
                model_kwargs={"dtype": "auto"},
                device="cpu",
            )
        except Exception as e:
            logger.error("Could not load LLM: %s", e)


FALLBACK_REPLY = "I don't have that information in our current listings."


def _build_context(context_properties: list) -> tuple[str, set]:
    if not context_properties:
        return "No properties are available.", set()

    known_titles = set()
    lines = ["=== PROPERTY DATABASE (this is ALL we have) ==="]
    for p in context_properties:
        known_titles.add(p.title.lower().strip())
        period_years = (p.investment_period / 12) if p.investment_period else 0
        lines.append(
            f"- Name: {p.title}\n"
            f"  Price: {p.price} MAD\n"
            f"  Min Investment: {p.min_investment} MAD\n"
            f"  Investment Period: {period_years:.0f} years ({p.investment_period} months)\n"
            f"  Risk Level: {p.risk_assessment}\n"
            f"  Rental Yield: {p.rental_yield}%\n"
            f"  Expected ROI: {p.expected_roi}%\n"
            f"  Location: {p.location}\n"
            f"  Type: {p.property_type}"
        )
    lines.append("=== END OF DATABASE ===")
    return "\n".join(lines), known_titles


def _passes_guardrail(reply: str, known_titles: set, context_properties: list = None) -> bool:
    logger.warning("DEBUG_GUARDRAIL - len(reply): %d, known_titles: %s", len(reply), known_titles)
    reply_lower = reply.lower()

    fabrication_signals = [
        "as a language model",
        "as an ai",
        "i cannot browse",
        "i'm sorry, but i",
        "depends on several factors",
        "consult with a financial advisor",
        "generally, it's important",
        "i'd be happy to help with general",
        "i can provide general",
        "i can help you find",
        "check with local",
        "visit their websites",
        "i'd recommend",
        "you might want to",
        "you could check",
        "local real estate agents",
        "it's important to check",
        "can vary depending",
        "contact a professional",
        "speak to an advisor",
        "in general,",
        "typically,",
        "it depends on",
        "please let me know your preferences",
        "provide your location",
        "feel free to ask",
    ]
    for signal in fabrication_signals:
        if signal in reply_lower:
            return False

    known_locations = set()
    if context_properties:
        for p in context_properties:
            if p.location:
                known_locations.add(p.location.strip().lower())

    foreign_cities = [
        "dubai", "paris", "london", "new york", "riyadh", "berlin",
        "madrid", "rome", "istanbul", "doha", "jeddah", "rabat",
        "fez", "agadir", "oujda", "meknes", "kenitra",
    ]
    for city in foreign_cities:
        if city in reply_lower and city not in known_locations and not any(city in t for t in known_titles):
            return False

    import re
    reply_percentages = set(re.findall(r'(\d+(?:\.\d+)?)\s*%', reply))
    if reply_percentages and context_properties:
        known_numbers = set()
        for p in context_properties:
            if p.rental_yield is not None:
                known_numbers.add(str(p.rental_yield))
            if p.expected_roi is not None:
                known_numbers.add(str(p.expected_roi))
        for pct in reply_percentages:
            if pct not in known_numbers and pct.rstrip('0').rstrip('.') not in {n.rstrip('0').rstrip('.') for n in known_numbers}:
                if float(pct) != 0:
                    return False

    if len(reply) > 100 and known_titles:
        logger.warning("Guardrail check: long reply. Known titles: %s", known_titles)
        has_title = any(title in reply_lower for title in known_titles)
        logger.warning("Guardrail check: has_title = %s", has_title)
        if not has_title:
            return False

    return True


def _build_property_summary(context_properties: list) -> str:
    if not context_properties:
        return FALLBACK_REPLY
    parts = ["Here are the properties we currently have:"]
    for p in context_properties:
        period_years = (p.investment_period / 12) if p.investment_period else 0
        parts.append(
            f"• {p.title} in {p.location} — "
            f"{p.rental_yield}% rental yield, "
            f"{p.expected_roi}% expected ROI, "
            f"{period_years:.0f}-year investment period, "
            f"risk level: {p.risk_assessment}."
        )
    return "\n".join(parts)


def generate_chat_reply(messages: list, context_properties: list) -> str:
    _load_model()

    if generator is None:
        return "The chatbot is currently unavailable."

    context_str, known_titles = _build_context(context_properties)

    system_prompt = (
        "You are a helpful real estate assistant for Igudar, a fractional "
        "investment platform in Morocco.\n\n"
        "Here is the property database you have access to:\n"
        f"{context_str}\n\n"
        "IMPORTANT RULES:\n"
        "1. Use ONLY the property data above to answer questions.\n"
        "2. If the user asks about a property or city NOT in the database, "
        "say exactly: 'I don't have that information in our current listings.'\n"
        "3. Never invent prices, yields, locations, or property names.\n"
        "4. Keep answers short (1-3 sentences).\n"
    )

    formatted_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        result = generator(
            formatted_messages,
            max_new_tokens=MAX_TOKENS,
            do_sample=True,
            temperature=0.05,
            return_full_text=False,
        )
        output = result[0]["generated_text"]

        if isinstance(output, list):
            reply = output[-1]["content"].strip()
        elif isinstance(output, str):
            reply = output.strip()
        else:
            reply = str(output)

        if not _passes_guardrail(reply, known_titles, context_properties):
            logger.warning("Guardrail blocked response: %s", reply[:120])
            return _build_property_summary(context_properties)

        return reply
    except Exception as e:
        logger.error("Generation error: %s", e)
        return "I encountered an error trying to process your request."
