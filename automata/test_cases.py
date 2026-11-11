"""Accepted / rejected test strings.  Each entry: (input, expected_accept, reason)."""

PASSWORD_CASES = [
    ("Secure@123", True, "All five conditions hold"),
    ("Abcdef1!", True, "Exactly 8 characters with all four classes"),
    ("P@ssw0rdLong", True, "Longer than the minimum"),
    ("9#xY7$kLm", True, "Classes in mixed order"),
    ("Srm_Trichy2026", True, "Underscore counts as a special character"),
    ("aB3$aB3$aB3$", True, "Repeated pattern is still valid format"),
    ("Ab1!", False, "Too short (4 characters)"),
    ("password123!", False, "No uppercase letter"),
    ("PASSWORD123!", False, "No lowercase letter"),
    ("Password!!", False, "No digit"),
    ("Password123", False, "No special character"),
    ("Pass word1!", False, "Contains a space (outside Σ)"),
    ("", False, "Empty string"),
]

EMAIL_CASES = [
    ("student@srmist.edu.in", True, "Sub-domains and a 2-letter extension"),
    ("sai.vardhan@gmail.com", True, "Dot inside the local part"),
    ("user_01@mail-server.org", True, "Underscore in local part, hyphen in domain"),
    ("a@b.co", True, "Shortest shapes of each part"),
    ("first-last@dept.university.ac.uk", True, "Several labels"),
    ("x9@123.info", True, "Numeric label followed by a letter extension"),
    ("plainaddress", False, "No @ symbol"),
    ("@gmail.com", False, "Empty local part"),
    ("user@gmail", False, "No dot / extension in the domain"),
    ("user..name@gmail.com", False, "Two separators in a row"),
    ("user@gmail.c", False, "Extension shorter than 2 letters"),
    ("user@@gmail.com", False, "Two @ symbols"),
    ("user@gmail.c0m", False, "Digit inside the extension"),
    ("user name@gmail.com", False, "Space is outside Σ"),
    ("user@-gmail.com", False, "Label starts with a hyphen"),
    ("user.@gmail.com", False, "Local part ends with a separator"),
]

PIN_CASES = [
    ("1234", True, "4 digits"),
    ("0000", True, "4 digits, leading zeros allowed"),
    ("987654", True, "6 digits"),
    ("000042", True, "6 digits with leading zeros"),
    ("5081", True, "4 digits"),
    ("314159", True, "6 digits"),
    ("123", False, "Too short (3 digits)"),
    ("12345", False, "5 digits is not a legal length"),
    ("1234567", False, "Too long (7 digits)"),
    ("12a4", False, "Contains a letter"),
    ("12 34", False, "Contains a space"),
    ("12#456", False, "Contains a special character"),
    ("", False, "Empty input"),
]
