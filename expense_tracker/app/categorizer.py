import re

CATEGORY_RULES = {
    "Food": [r"mcdonald", r"starbucks", r"tim hortons", r"pizza", r"restaurant", r"uber eats", r"doordash"],
    "Groceries": [r"walmart", r"costco", r"no frills", r"loblaws", r"grocery", r"freshco"],
    "Transport": [r"uber", r"lyft", r"gas", r"petro", r"shell", r"esso", r"parking", r"transit"],
    "Bills": [r"hydro", r"internet", r"phone", r"rogers", r"bell", r"rent", r"utilities"],
    "Shopping": [r"amazon", r"best buy", r"ikea", r"mall", r"store", r"shop"],
    "Health": [r"pharmacy", r"shoppers", r"clinic", r"dentist", r"hospital"],
    "Entertainment": [r"netflix", r"spotify", r"cinema", r"steam", r"playstation", r"xbox"],
}

def categorize(description: str) -> str:
    d = description.lower().strip()
    for cat, patterns in CATEGORY_RULES.items():
        for p in patterns:
            if re.search(p, d):
                return cat
    return "Other"
