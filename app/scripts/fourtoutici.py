import os
from typing import Dict, List, Tuple
import requests
import bs4
import json


def get_download_page_links(keyword: str) -> Tuple[List[Dict[str, str]], int]:
    """
    Une fonction cherchant le mot clef en en ligne et renvoyant la liste des liens vers
    les pages de téléchargement pour chaque résultat.


    Argument:
        keyword: str:
    Return:
        (list de lien, code de résultat https)

    """

    keyword_plus = "+".join(keyword.split(" "))

    r = requests.get(
        "http://www.fourtoutici.top/search.php?action=showsearchresults&q=+{0}&listyear=20xx&search=Recherche".format(keyword_plus))

    soup = bs4.BeautifulSoup(r.content, features="html.parser")

    # rows = soup.select("table > tbody td > img")

    if r.status_code == 200:
        results = soup.select("a")

        filtered_results = []
        for result in results:
            content = ""
            try:

                if result['href'][:len("javascript")] == "javascript":

                    url = result['href']

                    content = "[" + url[len("javascript:popupup")+1:-1] + "]"

                    # Problème, les ' dans les mots ne sont pas décodable par json.
                    # on les transforme en ""
                    content = content.replace("'", "\"")

                    json_content = json.loads(content)

                    row_dict = {
                        "title": json_content[0],
                        "directory": json_content[1]
                    }

                    filtered_results.append(row_dict)
            except Exception as e:
                print(e, content)

        return (filtered_results, 200)

    else:
        print("Impossible d'accéder au serveur")
        return ([], r.status_code)


def download_file(title: str, directory: str, output_dir: str) -> str:
    """
    Download a file from the website solving the little number puzzle

    return downloaded file path 
    None if errror
    """

    download_link = "http://www.fourtoutici.top/upload.php?action=downloadfile&filename={0}&directory={1}&".format(
        title, directory)

    r = requests.get(download_link)

    if r.status_code != 200:
        print("impossible to reach: error cde", r.status_code)
        return None

    soup = bs4.BeautifulSoup(r.content, features="html.parser")

    try:
        raw_code = None
        images = soup.select("img")
    except:
        print("impossible to get img tag in download page")
        return None

    for image in images:
        try:
            if image["alt"] == "Code de sécurité à recopier":
                raw_code = image["src"].split("?")[-1]
                break
        except:
            pass

    # todo, reanalyse first
    first = "6"
    center = raw_code[-2:]
    last = raw_code[-3]
    code = first + center + last

    print("attempting to beat code ", raw_code, " with ", code)

    download_link = "http://www.fourtoutici.top/upload.php?action=download&directory={1}&filename={0}&".format(
        title.replace(" ", "+"), directory)

    file_download_link = download_link + "valcodeup=" + code

    r = requests.get(file_download_link)

    if r.status_code != 200:
        print("impossible to reach file ", r.status_code)
        return None

    output_file = os.path.join(output_dir, title)

    print(">> saving to ", output_file)

    with open(output_file, "wb+") as f:
        f.write(r.content)

    return output_file


"""

exemple d'utilisation

filtered_results, error_code = get_download_page_links("les sables")

chosen_result = filtered_results[0]

download_file(chosen_result['title'], chosen_result['directory'])
"""

"""

1605135763 6637
1605135819 6198
1605135972 6729

on en déduit que
les chiffres au centre de l'image sont les chiffre de fin du code
dernier chiffre de l'image = code[-3]

"""
