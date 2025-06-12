def month_to_integer(month: str) -> int | None:
    month = month.lower().strip().rstrip()
    for i, matches in enumerate(MONTH_MATCHES):
        if month in matches:
            return i + 1
    return None


MONTH_MATCHES = [
    ["jan", "january", "januar"],
    ["feb", "february", "februar"],
    ["mar", "march", "mart"],
    ["apr", "april"],
    ["may", "maj"],
    ["jun", "june"],
    ["jul", "july"],
    ["aug", "avg", "august", "avgust"],
    ["sep", "september", "septembar"],
    ["oct", "okt", "october", "oktobar"],
    ["nov", "november", "novembar"],
    ["dec", "december", "decembar"],
]
