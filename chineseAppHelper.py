#!/usr/bin/env python3
import json
import argparse
import sys
import re

# Define common punctuation and whitespace characters to ignore in logging.
# Added the full-width quotation marks “ and ”
PUNCTUATION_AND_WHITESPACE = set(" \t\n\r\f\v，。？！、：；《》【】（）“”")


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
    
    # Store consecutive unknown Hanzi characters for grouped logging
    unknown_hanzi_sequence = []
    
    # NEW: List to accumulate all sequences for a single, final log message
    all_unknown_sequences = []

    while i < n:
        matched = False

        # Try a 4-char, then 3-char, then 2-char, then 1-char match
        for L in range(max_len, 0, -1):
            if i + L > n:
                continue

            chunk = story[i:i+L]

            if chunk in dict_map:
                # --- Known Token Found ---
                
                # If there's an accumulated unknown sequence, save it and clear the accumulator
                if unknown_hanzi_sequence:
                    all_unknown_sequences.append("".join(unknown_hanzi_sequence))
                    unknown_hanzi_sequence = []
                
                # Add the known token
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
            # Punctuation/Whitespace: Ignore, but check for prior unknown sequence
            
            # If there's an accumulated unknown sequence, save it and clear the accumulator
            if unknown_hanzi_sequence:
                all_unknown_sequences.append("".join(unknown_hanzi_sequence))
                unknown_hanzi_sequence = []
            
            # Add the punctuation/whitespace token (id: None)
            tokens.append({
                "id": None,
                "text": ch
            })

        else:
            # Unknown Hanzi character: Accumulate
            unknown_hanzi_sequence.append(ch)
            tokens.append({
                "id": None,
                "text": ch
            })

        i += 1

    # Final check after loop ends for any remaining unknown Hanzi sequence
    if unknown_hanzi_sequence:
        all_unknown_sequences.append("".join(unknown_hanzi_sequence))

    # NEW: Log all accumulated unknown sequences in the desired format
    log_final_unknown_sequences(all_unknown_sequences)

    # Build output structure
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
    """
    Logs all unknown sequences accumulated during tokenization in a single,
    comma-separated line.
    """
    if not all_sequences:
        return

    # Join the individual sequences (e.g., '决' and '定' become '决定')
    # Then join all the resulting multi-character sequences with ', '
    log_output = ", ".join(all_sequences)
    print(f"[WARN] All Unknown Hanzi: {log_output}")


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
