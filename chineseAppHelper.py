#!/usr/bin/env python3
import json
import argparse
import sys
import re

# Define common punctuation and whitespace characters to ignore in logging.
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
# Tokenize story → output.json
# Using longest match: 4 → 3 → 2 → 1 characters
# --------------------------------------------------------
def tokenize_story(dict_path, story_path, character_names):
    dict_map = load_dictionary(dict_path)

    with open(story_path, "r", encoding="utf-8") as f:
        story = f.read().strip()

    tokens = []
    max_len = 4
    i = 0
    n = len(story)
    
    # Store consecutive unknown Hanzi characters for grouped logging
    unknown_hanzi_sequence = []
    
    # List to accumulate all sequences for a single, final log message
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
                
                # Log the name being tokenized
                print(f"[INFO] Character Name Tokenized: {chunk}")
                
                # If there's an accumulated unknown sequence, save it and clear the accumulator
                if unknown_hanzi_sequence:
                    all_unknown_sequences.append("".join(unknown_hanzi_sequence))
                    unknown_hanzi_sequence = []
                
                # Add the name token (id: None)
                tokens.append({
                    "id": None,
                    "text": chunk
                })
                i += L
                matched = True
                break
            
            # 2. Check if the chunk is in the dictionary (Second Priority)
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

    # Log all accumulated unknown sequences in the desired format
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
        description="Chinese Story Tokenizer (Longest-Match Algorithm)"
    )

    # Positional arguments (required)
    parser.add_argument("dict", help="Path to dictionary.json")
    parser.add_argument("story", help="Path to story.txt")
    
    # Optional argument for character names
    parser.add_argument(
        "--names",
        default="",
        help="Comma-separated list of character names to tokenize as 'null' (e.g., 王小明,李华)"
    )

    args = parser.parse_args()

    # Parse the comma-separated string into a set for quick lookup
    # Handle case where --names is empty
    if args.names:
        character_names = set(args.names.split(','))
    else:
        character_names = set()

    # The action is now always tokenization
    tokenize_story(args.dict, args.story, character_names)


if __name__ == "__main__":
    main()
