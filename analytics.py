import re

def password_strength(password):
    """
    Returns a score and message for password strength
    """
    score = 0
    # Length check
    if len(password) >= 8:
        score += 1
    # Uppercase
    if re.search(r"[A-Z]", password):
        score += 1
    # Lowercase
    if re.search(r"[a-z]", password):
        score += 1
    # Numbers
    if re.search(r"[0-9]", password):
        score += 1
    # Special characters
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1

    # Message based on score
    if score <= 2:
        msg = "Weak"
    elif score == 3 or score == 4:
        msg = "Medium"
    else:
        msg = "Strong"

    return score, msg
