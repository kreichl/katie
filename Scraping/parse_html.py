import os
import io
from bs4 import BeautifulSoup

name = "2465-Tilton-Ln_Brookfield_WI_53045_M74918-55816"
fname = os.path.join("Scraping", "HTML_files", f"{name}.html")

with io.open(fname, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

text = soup.get_text()

with io.open(os.path.join("Scraping", "text_files", f"{name}.txt"), "w", encoding="utf-8") as f:
    f.write(text)