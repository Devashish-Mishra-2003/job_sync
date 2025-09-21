def parse_name_email_from_text(text):
    lines = text.splitlines(); name=''; email=''
    for l in lines[:8]:
        if '@' in l and '.' in l:
            parts = l.strip().split()
            for p in parts:
                if '@' in p and '.' in p: email=p; break
        elif len(l.strip().split())<=4 and len(l.strip())>2 and name=='' and '@' not in l:
            name = l.strip()
    return name, email
