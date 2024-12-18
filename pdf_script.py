from pypdf import PdfReader 

def first_read():
    reader = PdfReader("peak-of-eloquence-sayings.pdf")

    text = ""

    for page in reader.pages:
        text += page.extract_text()

    print(text)

def ends_saying(line: str):
    return line.endswith(".") or line.endswith(". ")

def starts_footer(line: str):
    return "                  " in line

def starts_saying(line: str):
    return "Imam Ali ibn Abu Talib ( x) said:" in line

def sanitized_read():
    with open("poe-s.txt") as file:
        lines = file.readlines()

    saying_start = False

    sanitized_text = ""
    for line in lines:
        if starts_saying(line):
            saying_start = True 
        if starts_footer(line) or ends_saying(line):
            saying_start = False

        if saying_start:
            sanitized_text += line
    f = open("poe.txt", "w")
    f.write(sanitized_text)

def parition_text():
    with open("peak-of-eloquence.txt") as file:
        lines = file.readlines()

    final_text = ""

    for line in lines:
        if ". " in line[:6]:
            final_text += "\n" + line[:-1]
        else:
            final_text += line[:-1]

    f = open("poe.txt", "w")
    f.write(final_text)

parition_text()
