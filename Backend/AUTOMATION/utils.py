def extract_title_from_command(command: str) -> str:
    cmd = (command or "").strip().lower()
    if '"' in command:
        parts = command.split('"')
        if len(parts) >= 3:
            return parts[1].strip()
    if "'" in command:
        parts = command.split("'")
        if len(parts) >= 3:
            return parts[1].strip()
    keywords = ["play", "open", "click", "watch", "search"]
    for kw in keywords:
        if kw in cmd:
            after = command.lower().split(kw, 1)[1]
            for rm in ["the", "video", "on youtube", "on you tube"]:
                after = after.replace(rm, "")
            title = after.strip(" :,-")
            if title and not title.replace(" ", "").isdigit():
                return title
    return ""