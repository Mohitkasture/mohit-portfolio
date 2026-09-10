from home.services.llm import chat_completion
from home.models import GameNpc


def npc_reply(message, npc_name="guide"):
    npc = GameNpc.objects.filter(name=npc_name, is_active=True).first()
    if not npc:
        npc = GameNpc(
            name="guide",
            display_name="Portfolio Guide",
            persona=(
                "You are a friendly game NPC inside Mohit's portfolio. "
                "You know he is a Python/Django backend developer who also builds AI features and games. "
                "Keep answers short and playful, 2-3 sentences."
            ),
            greeting="Hey traveler — ask me about Mohit's backend quests, AI gear, or game builds.",
        )

    reply = chat_completion(
        [
            {"role": "system", "content": npc.persona},
            {"role": "user", "content": message},
        ],
        temperature=0.6,
        max_tokens=220,
    )
    if not reply:
        reply = (
            f"{npc.display_name}: Mohit builds Django APIs, AI-backed portfolio tools, "
            "and experiments with game NPCs like me. Ask about Flowcreator or his backend stack!"
        )
    return {
        "npc": npc.display_name if hasattr(npc, "display_name") else "Portfolio Guide",
        "reply": reply,
        "greeting": getattr(npc, "greeting", ""),
    }
