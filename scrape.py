# beauty_soup.py

from bs4 import BeautifulSoup
from urllib.request import urlopen

url = "https://nl.wikipedia.org/wiki/ADO_Den_Haag_in_het_seizoen_2021/22_(mannen)"
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, features="html.parser")

paragraphs = soup.find_all('li')

    # Extract words from the paragraphs
words = []
for paragraph in paragraphs:
    words += paragraph.get_text().split()

file = open("test.txt", 'a', encoding="utf8")

count = 0
for i in range(0, len(words), 15):
    if(count == 500):
        break
    if(len(words)<i+15):
        break
    line = ""
    for word in words[i:i+15]:
        line += " " + word
    file.write(f"nl|{line}\n")
    count += 1

file.close()

print("Done")

# en:https://en.wikipedia.org/wiki/History_of_China
# en:
# nl:https://nl.wikipedia.org/wiki/Geschiedenis_van_China 

