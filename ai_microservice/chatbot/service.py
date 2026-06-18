from transformers import pipeline
import os

MODEL_NAME = os.getenv("CHAT_MODEL_NAME", "Qwen/Qwen2.5-0.5B-Instruct")
generator = None


def _load_model():
    global generator
    if generator is not None:
        return

    try:
        generator = pipeline(
            "text-generation",
            model=MODEL_NAME,
            model_kwargs={"torch_dtype": "auto"},
        )
    except Exception as e:
        print(f"Could not load LLM: {e}")


def generate_chat_reply(messages: list, context_properties: list) -> str:
    _load_model()

    if generator is None:
        return "The chatbot is currently unavailable."

    if context_properties:
        context_str = "Available Properties:\n"
        for p in context_properties:
            context_str += (
                f"- {p.title} (ID {p.id}): {p.description[:150]}... "
                f"Min Investment: {p.min_investment} MAD, "
                f"Lock-in: {p.lock_in_years} years, "
                f"Risk: {p.risk_rating}.\n"
            )
    else:
        context_str = "No specific properties found matching the query."

    system_prompt = (
        "You are a helpful, professional real estate assistant for Igudar, "
        "a fractional investment platform in Morocco.\n"
        "Always use the following property context to answer the user's "
        "questions. If the user asks about something not in the context, "
        "politely let them know you only have information about Igudar's "
        "current inventory.\n\n"
        f"{context_str}"
    )

    formatted_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        result = generator(
            formatted_messages,
            max_new_tokens=250,
            do_sample=True,
            temperature=0.6,
        )
        output = result[0]["generated_text"]

        if isinstance(output, list):
            return output[-1]["content"].strip()
        elif isinstance(output, str):
            return output.strip()
        return str(output)
    except Exception as e:
        print(f"Generation error: {e}")
        return "I encountered an error trying to process your request."
