import re
from collections import Counter


def process_text(text):
    try:
        words = re.findall(r'\b\w+\b', text.lower())  # Extract words
        word_count = Counter(words)
        return word_count
    except Exception as e:
        return f"Processing Error: {e}"


if __name__ == "__main__":
    text = input("Enter text: ")
    print(process_text(text))
