#!/usr/bin/env python3
import json
import argparse
import sys
import os

# Define common punctuation and whitespace characters to ignore in logging.
PUNCTUATION_AND_WHITESPACE = set(" \t\n\r\f\v，。？！、：；《》【】（）“”")

# Hard-coded file paths
DICT_FILE = "dictionary.json"
STORY_FILE = "story.txt"

def load_dictionary(dict_path):
    if not os.path.exists(dict_path):
        print(f"[ERROR] {dict_path} not found in the current directory.")
        sys.exit(1)
    with open(dict_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dict_map = {}
    for wid, entry in data.items():
        hanzi = entry["hanzi"]
        dict_map[hanzi] = wid

    return dict_map

def tokenize_story(character_names):
    dict_map = load_dictionary(DICT_FILE)

    if not os.path.exists(STORY_FILE):
        print(f"[ERROR] {STORY_FILE} not found in the current directory.")
        sys.exit(1)

    with open(STORY_FILE, "r", encoding="utf-8") as f:
        story = f.read().strip()

    tokens = []
    max_len = 4
    i = 0
    n = len(story)
    
    unknown_hanzi_sequence = []
    all_unknown_sequences = []

    while i < n:
        matched = False
        
        # Try a 4-char, then 3-char, then 2-char, then 1-char match
        for L in range(max_len, 0, -1):
            if i + L > n:
                continue

            chunk = story[i:i+L]

            # 1. Check if the chunk is a known character name (Highest Priority)
            if chunk in character_names:
                print(f"[INFO] Character Name Tokenized: {chunk}")
                
                if unknown_hanzi_sequence:
                    all_unknown_sequences.append("".join(unknown_hanzi_sequence))
                    unknown_hanzi_sequence = []
                
                tokens.append({
                    "id": "w05005",
                    "text": chunk
                })
                i += L
                matched = True
                break
            
            # 2. Check if the chunk is in the dictionary (Second Priority)
            if chunk in dict_map:
                if unknown_hanzi_sequence:
                    all_unknown_sequences.append("".join(unknown_hanzi_sequence))
                    unknown_hanzi_sequence = []
                
                tokens.append({
                    "id": dict_map[chunk],
                    "text": chunk
                })
                i += L
                matched = True
                break

        if matched:
            continue

        # --- No Match (Unknown Token) Found ---
        ch = story[i]

        if ch in PUNCTUATION_AND_WHITESPACE:
            if unknown_hanzi_sequence:
                all_unknown_sequences.append("".join(unknown_hanzi_sequence))
                unknown_hanzi_sequence = []
            
            tokens.append({
                "id": None,
                "text": ch
            })
        else:
            unknown_hanzi_sequence.append(ch)
            tokens.append({
                "id": None,
                "text": ch
            })

        i += 1

    if unknown_hanzi_sequence:
        all_unknown_sequences.append("".join(unknown_hanzi_sequence))

    log_final_unknown_sequences(all_unknown_sequences)

    output = {
        "storyId": "",
        "title": "",
        "subtitle": "",
        "difficulty": 1,
        "topic": "",
        "tokens": tokens
    }

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("[OK] Wrote tokenized story → output.json")

def log_final_unknown_sequences(all_sequences):
    if not all_sequences:
        return
    log_output = ", ".join(all_sequences)
    print(f"[WARN] All Unknown Hanzi: {log_output}")

def main():
    parser = argparse.ArgumentParser(
        description="Chinese Story Tokenizer (Using local dictionary.json and story.txt)"
    )

    parser.add_argument(
        "--names",
        default="",
        help="Comma-separated list of character names (e.g., 王小明,李华)"
    )

    args = parser.parse_args()

    if args.names:
        character_names = set(args.names.split(','))
    else:
        character_names = set()

    tokenize_story(character_names)

if __name__ == "__main__":
    main()
