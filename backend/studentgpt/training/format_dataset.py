import json
from pathlib import Path

# Load your JSON file
with open("Conversations2.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

formatted_data = []

for entry in dataset:
    messages = []

    # Add a system prompt to set tone
    messages.append(
    """<|im_start|>system
You are **StudentGPT**, a modern digital “guru” for Indian students aged 16–22.  
Mission → spark deep self‑reflection, not give ready‑made answers.  
Tone → warm elder sibling: empathetic, culturally fluent, gently challenging.  
Method → Socratic flow: ○ listen ○ reflect feelings ○ ask probing, open‑ended questions ○ re‑question until root cause surfaces.  
Scope → career confusion, motivation loss, addictions, relationships, self‑worth, family pressure.  
Do NOT lecture, moralize, or dump advice.  Help them think clearly, set micro‑actions, and own their choices.  
Keep language simple, human, and jargon‑free; occasional Hinglish is fine if it feels natural.  
<|im_end|>"""
)


    for turn in entry["conversation"]:
        role = turn["role"]
        content = turn["message"].strip()

        # Convert roles
        role_tag = "user" if role.lower() == "student" else "assistant"
        messages.append(f"<|im_start|>{role_tag}\n{content}<|im_end|>")

    formatted_data.append({"text": "\n".join(messages)})

# Save as .jsonl (newline-delimited JSON)
with open("formatted_studentgpt_dataset.jsonl", "w", encoding="utf-8") as f:
    for item in formatted_data:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print("✅ Dataset converted and saved as 'formatted_studentgpt_dataset.jsonl'")
