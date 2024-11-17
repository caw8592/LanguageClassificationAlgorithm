# beauty_soup.py

from bs4 import BeautifulSoup
from urllib.request import urlopen

LINE_NUM = 500

for j in range(2):
    count = 0
    while(True):
        if(count == LINE_NUM):
            break
        if j == 0:
            url = "https://en.wikipedia.org/wiki/Special:Random"
        else:
            url = "https://nl.wikipedia.org/wiki/Special:Random"
        page = urlopen(url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, features="html.parser")

        paragraphs = soup.find_all('p')

        words = []
        for paragraph in paragraphs:
            words += paragraph.get_text().split()

        file = open("test.txt", 'a', encoding="utf8")

        for i in range(0, len(words), 15):
            if(count == LINE_NUM):
                break
            if(len(words)<i+15):
                break
            line = ""
            for word in words[i:i+15]:
                line += " " + word
            if not "·" in line:
                if j == 0:
                    file.write(f"en|{line}\n")
                else:
                    file.write(f"nl|{line}\n")
                count += 1

        file.close()

print("Done")


