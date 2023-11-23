import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
import lxml
import json

def get_ip_from_2ip():

    s = requests.Session()
    response = s.get('https://2ip.ru/', headers=Headers().generate())

    src = response.text

    # with open('index.html', 'w', encoding='utf-8') as file:
    #     file.write(response.text)

    # with open('index.html', 'r', encoding='utf-8') as file:
    #     src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    ip_div = soup.find("div", id="d_clip_button")
    ip = ip_div.find("span")

    return ip.text


def get_timezone_from_geoip2_precision_demo(ip):


    with requests.session() as session:

        headers = Headers()

        response = session.get("https://www.maxmind.com/en/geoip2-precision-demo", headers=headers.generate())

        src = response.text
        # with open("csrf_find.html", "w", encoding="utf-8") as file:
        #     file.write(response.text)

        # with open("csrf_find.html", "r", encoding="utf-8") as file:
        #     src = file.read()

        src = BeautifulSoup(src, 'lxml')

        scripts = src.find_all("script")

        x_csrf_token = scripts[2].text.split("\n")[2].replace(' "','').replace('";','').split("=")[1]
        

        cookies = response.cookies.get_dict()

        response = session.post('https://www.maxmind.com/en/geoip2/demo/token', cookies=cookies, headers={'x-csrf-token': x_csrf_token})

        response_json = json.loads(response.content)
        token = response_json["token"]

        url_for_time_zone = f'https://geoip.maxmind.com/geoip/v2.1/city/{ip}?demo=1'

        response = requests.get(url_for_time_zone, cookies=cookies, headers={'x-csrf-token': x_csrf_token, 'Authorization': f'Bearer {token}'})

        response_json = json.loads(response.content)
        time_zone = response_json['location']['time_zone']


    return time_zone


def get_list_regions_in_time_zone(time_zone):
    response = requests.get("https://gist.github.com/salkar/19df1918ee2aed6669e2")

    src = response.text
    # with open('list_regions.html', 'w', encoding='utf-8') as file:
    #     file.write(response.text)

    # with open('list_regions.html', 'r', encoding='utf-8') as file:
    #     src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    table = soup.find("table", attrs={"data-tagsearch-path": "Timezones for Russian regions"})
    trs = table.find_all("tr")
    
    regions = []

    for count, value in enumerate(trs):
        if count == 0 or count == len(trs)-1:
            continue
        td = value.find_all("td")
        regions.append(td[1].text.replace('"','').replace("  [","").replace("],","").replace("]","").split(", "))
    
    regions_str = ""
    for index, r in enumerate(regions):
        if r[1] == time_zone:
            if index != len(regions)-1:
                regions_str += f"{r[0]}, "
            else:
                regions_str += f"{r[0]}"

    with open('result.txt', 'w', encoding='utf-8') as file:
        file.write(f"{time_zone}\n")
        file.write(regions_str)



def main():
    ip_address = get_ip_from_2ip()
    time_zone = get_timezone_from_geoip2_precision_demo(ip_address)
    get_list_regions_in_time_zone(time_zone)



if __name__ == '__main__':
    main()