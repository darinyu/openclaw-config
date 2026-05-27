#!/usr/bin/env python3
"""Vocabulary quiz tool - pick random words and quiz Darin"""
import json, random, sys
from pathlib import Path

DATA = Path(__file__).parent / "words.json"

def load():
    return json.loads(DATA.read_text())

def save(data):
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def pick_quiz(n=3):
    data = load()
    words = data["words"]
    if not words:
        return "单词本还是空的！还没有记过单词 📖"
    
    # Prefer words that haven't been quizzed recently
    quizzed_ids = {h["word_id"] for h in data["quiz_history"][-20:]}
    unquizzed = [w for w in words if w["id"] not in quizzed_ids]
    pool = unquizzed or words
    
    selected = random.sample(pool, min(n, len(pool)))
    return selected

def record_quiz_result(word_ids, correct_count):
    data = load()
    for wid in word_ids:
        data["quiz_history"].append({"word_id": wid, "date": __import__("datetime").date.today().isoformat()})
    # Update word stats
    for w in data["words"]:
        if w["id"] in word_ids:
            w["times_quizzed"] = w.get("times_quizzed", 0) + 1
    save(data)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "quiz"
    if cmd == "quiz":
        words = pick_quiz(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
        if isinstance(words, str):
            print(words)
        else:
            for w in words:
                pron = f"  [{w.get('pronunciation', '')}]" if w.get('pronunciation') else ""
                print(f"  {w['word']}{pron}")
            print("---")
            for w in words:
                pron = f" [{w.get('pronunciation', '')}]" if w.get('pronunciation') else ""
                print(f"  {w['word']}{pron} — {w['meaning']}")
    elif cmd == "add":
        word = sys.argv[2]
        meaning = sys.argv[3]
        pron = sys.argv[4] if len(sys.argv) > 4 else ""
        source = sys.argv[5] if len(sys.argv) > 5 else ""
        data = load()
        data["words"].append({
            "id": f"w{len(data['words'])+1}",
            "word": word,
            "meaning": meaning,
            "pronunciation": pron,
            "source": source,
            "times_quizzed": 0,
            "added": __import__("datetime").date.today().isoformat()
        })
        save(data)
        print(f"Added: {word} — {meaning}")
