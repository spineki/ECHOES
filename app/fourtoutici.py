import requests
import bs4
import json
r = requests.get(
    "http://www.fourtoutici.top/search.php?action=showsearchresults&q=+BrandoN+mull&listyear=20xx&search=Recherche")

soup = bs4.BeautifulSoup(r.content, features="html.parser")

print(r.status_code)

results = soup.select("a")


filtered_results = []
for result in results:
    try:
        url = ""
        content = ""
        if result['href'][:len("javascript")] == "javascript":

            url = result['href']

            content = "[" + url[len("javascript:popupup")+1:-1] + "]"
            content = content.replace("'", "\"")

            filtered_results.append(json.loads(content))
    except Exception as e:
        print(e, content)

chosen_result = filtered_results[0]


download_link = "http://www.fourtoutici.top/upload.php?action=downloadfile&filename={0}&directory={1}&".format(
    chosen_result[0], chosen_result[1])
"http://www.fourtoutici.top/upload.php?action=download&directory={}&filename={}&valcodeup=6"
r = requests.get(download_link)

soup = bs4.BeautifulSoup(r.content, features="html.parser")

raw_code = None
images = soup.select("img")
for image in images:
    try:
        if image["alt"] == "Code de sécurité à recopier":
            raw_code = image["src"].split("?")[-1]
            break
    except:
        pass

print(raw_code)

# todo, reanalyse first
first = "6"
center = raw_code[-2:]
last = raw_code[-3]
code = first + center + last

print(code)

print(download_link)

download_link = "http://www.fourtoutici.top/upload.php?action=download&directory={1}&filename={0}&".format(
    chosen_result[0].replace(" ", "+"), chosen_result[1])


file_download_link = download_link + "valcodeup=" + code
print(file_download_link)
r = requests.get(file_download_link)
print(r.status_code)

with open("export.epub", "wb+") as f:
    f.write(r.content)


"""

1605135763 6637
1605135819 6198
1605135972 6729

on en déduit que
les chiffres au centre de l'image sont les chiffre de fin du code
dernier chiffre de l'image = code[-3]


valcodeup
"""
