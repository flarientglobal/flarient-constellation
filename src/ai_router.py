"""AI router — tries external free AI providers, falls back to deterministic templates."""
import json, os, urllib.request

TIMEOUT = 15

def _try_groq(prompt):
    key = os.environ.get("GROQ_API_KEY", "")
    if not key: return None
    try:
        body = json.dumps({"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300, "temperature": 0.7}).encode()
        req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
            return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        print(f"[AI] Groq failed: {e}")
        return None

def _try_cloudflare(prompt):
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    if not token or not account_id: return None
    try:
        body = json.dumps({"messages": [{"role": "user", "content": prompt}], "max_tokens": 300}).encode()
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/meta/llama-3.1-8b-instruct"
        req = urllib.request.Request(url, data=body, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
            return data.get("result", {}).get("response", "").strip()
    except Exception as e:
        print(f"[AI] Cloudflare failed: {e}")
        return None

def _template_summary(event):
    et = event.get("event_type", "event")
    sev = event.get("severity", "")
    summary = event.get("summary", "Space weather event detected.")
    return f"{sev} {et.replace('_', ' ')}: {summary} See flarient.com for details."

def generate_summary(event):
    prompt = (
        f"Write a concise 1-2 sentence plain-English summary of this space weather event for a general audience. "
        f"Do not use hashtags or emojis.\n\nEvent type: {event.get('event_type')}\nSeverity: {event.get('severity', 'unknown')}\n"
        f"Summary: {event.get('summary', '')}\nCurrent value: {event.get('current_value')}\nPrevious value: {event.get('previous_value')}\n\nRespond with just the summary text."
    )
    for provider_fn in [_try_groq, _try_cloudflare]:
        result = provider_fn(prompt)
        if result and len(result) > 10:
            return result, "ai"
    return _template_summary(event), "template"