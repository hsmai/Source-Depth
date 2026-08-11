"""Yes/No 대표 토큰 id 확정 + logit 판정 (브리프 B-3)."""
import json

from ..config import TOKEN_IDS_JSON
from ..runlog import blocked, iso_now


def resolve_yes_no_ids(model, processor, probe_inputs: list, log_path=None):
    """소량 생성으로 실제 첫 토큰을 관측해 Yes/No id 집합 확정 (B-3 요구)."""
    tok = processor.tokenizer
    observed = []
    for inp in probe_inputs:
        gen = model.generate(**inp, max_new_tokens=5, do_sample=False)
        prompt_len = inp["input_ids"].shape[1]
        first_id = gen[0, prompt_len].item()
        text = tok.decode(gen[0, prompt_len:], skip_special_tokens=True)
        observed.append({"first_id": first_id,
                         "first_tok": tok.decode([first_id]), "gen_text": text})
    yes_ids, no_ids = set(), set()
    for o in observed:
        w = o["first_tok"].strip().lower()
        if w == "yes":
            yes_ids.add(o["first_id"])
        elif w == "no":
            no_ids.add(o["first_id"])
    for variants, target in ((["Yes", " Yes", "yes", " yes", "YES"], yes_ids),
                             (["No", " No", "no", " no", "NO"], no_ids)):
        for s in variants:
            enc = tok.encode(s, add_special_tokens=False)
            if len(enc) == 1:
                target.add(enc[0])
    if not yes_ids or not no_ids or (yes_ids & no_ids):
        blocked("yesno", "Yes/No 토큰 집합 확정 실패",
                {"yes": sorted(yes_ids), "no": sorted(no_ids), "observed": observed})
    payload = {"yes_ids": sorted(yes_ids), "no_ids": sorted(no_ids),
               "observed": observed, "ts": iso_now()}
    TOKEN_IDS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_IDS_JSON, "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    if log_path:
        with open(log_path, "w") as f:
            json.dump(observed, f, ensure_ascii=False, indent=1)
    return sorted(yes_ids), sorted(no_ids)


def load_yes_no_ids():
    if not TOKEN_IDS_JSON.exists():
        blocked("yesno", "token_ids.json 부재 — 스모크 미실행", {})
    with open(TOKEN_IDS_JSON) as f:
        d = json.load(f)
    return d["yes_ids"], d["no_ids"]


def predict(last_logits, yes_ids, no_ids) -> dict:
    """마지막 프롬프트 위치 next-token logits에서 max-logit 비교 (B-3). 동률→no (사전 규정)."""
    ly = last_logits[yes_ids].max().item()
    ln = last_logits[no_ids].max().item()
    return {"pred": "yes" if ly > ln else "no",
            "logit_yes": round(ly, 4), "logit_no": round(ln, 4),
            "margin": round(ly - ln, 4), "tie": ly == ln}
