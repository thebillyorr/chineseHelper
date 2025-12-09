#!/usr/bin/env python3
import json
import argparse
import sys


# --------------------------------------------------------
# Load dictionary: returns dict_map["我"] = "w00001"
# --------------------------------------------------------
def load_dictionary(dict_path):
    with open(dict_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dict_map = {}
    for wid, entry in data.items():
        hanzi = entry["hanzi"]
        dict_map[hanzi] = wid

    return dict_map


# --------------------------------------------------------
# PART 1: Extract comma-separated Hanzi → output.txt
# --------------------------------------------------------
def extract_hanzi(dict_path):
    with open(dict_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    hanzi_list = [entry["hanzi"] for entry in data.values()]
    result = ", ".join(hanzi_list)

    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(result)

    print("[OK] Wrote comma-separated hanzi list → output.txt")


# --------------------------------------------------------
# PART 2: Tokenize story → output.json
# Using longest match: 4 → 3 → 2 → 1 characters
# --------------------------------------------------------
def tokenize_story(dict_path, story_path):
    dict_map = load_dictionary(dict_path)

    with open(story_path, "r", encoding="utf-8") as f:
        story = f.read().strip()

    tokens = []
    max_len = 4
    i = 0
    n = len(story)

    while i < n:
        matched = False

        # Try a 4-char, then 3-char, then 2-char, then 1-char match
        for L in range(max_len, 0, -1):
            if i + L > n:
                continue

            chunk = story[i:i+L]

            if chunk in dict_map:
                tokens.append({
                    "id": dict_map[chunk],
                    "text": chunk
                })
                i += L
                matched = True
                break

        if matched:
            continue

        # No match even for 1 char → unknown token
        ch = story[i]
        print(f"[WARN] Unknown token: '{ch}'")
        tokens.append({
            "id": None,
            "text": ch
        })
        i += 1

    # Build output structure
    output = {
        "storyId": "",
        "title": "",
        "difficulty": 1,
        "topic": "",
        "tokens": tokens
    }

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("[OK] Wrote tokenized story → output.json")


# --------------------------------------------------------
# CLI
# --------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Chinese Dictionary & Story Processing Helper"
    )

    parser.add_argument(
        "--hanzi",
        action="store_true",
        help="Extract comma-separated hanzi from dictionary.json → output.txt"
    )

    parser.add_argument(
        "--token",
        action="store_true",
        help="Tokenize a story using longest-match algorithm → output.json"
    )

    parser.add_argument("dict", help="Path to dictionary.json")
    parser.add_argument("input", nargs="?", help="Path to story.txt (required for --token mode)")

    args = parser.parse_args()

    # Validate mode selection
    if args.hanzi and args.token:
        print("[ERROR] Cannot use both --hanzi and --token at the same time.")
        sys.exit(1)

    if not args.hanzi and not args.token:
        print("[ERROR] You must specify either --hanzi or --token.")
        sys.exit(1)

    # Extract hanzi → no input file needed
    if args.hanzi:
        extract_hanzi(args.dict)
        return

    # Tokenize story → requires input
    if args.token:
        if not args.input:
            print("[ERROR] Token mode requires: dictionary.json story.txt")
            sys.exit(1)
        tokenize_story(args.dict, args.input)
        return


if __name__ == "__main__":
    main()
