def generate_text(length=100):
    import random
    import string

    words = ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog', 'lorem', 'ipsum', 'dolor', 'sit', 'amet']
    text = ' '.join(random.choices(words, k=length))
    return text

def calculate_wpm(expected_text, typed_text, elapsed_time):
    """
    Calculate WPM based only on the number of correct words typed.
    """
    expected_words = expected_text.split()
    typed_words = typed_text.split()

    # Count the number of correctly typed words
    correct_words = sum(1 for ew, tw in zip(expected_words, typed_words) if ew == tw)

    # Calculate WPM based on correct words
    minutes = elapsed_time / 60
    return correct_words / minutes if minutes > 0 else 0

def calculate_accuracy(expected_text, typed_text):
    """
    Calculate the accuracy of the typed text compared to the expected text.
    """
    expected_words = expected_text.split()
    typed_words = typed_text.split()

    correct_words = sum(1 for ew, tw in zip(expected_words, typed_words) if ew == tw)
    total_words = len(expected_words)

    return (correct_words / total_words) * 100 if total_words > 0 else 0

def get_current_time():
    import time
    return time.time()