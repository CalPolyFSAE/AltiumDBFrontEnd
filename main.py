import json
import urllib.request


def main():
    url = 'https://octopart.com/api/v3/parts/search?'
    url += '&queries=[{"mpn":"SN74S74N","offers.seller.name":"Digi-Key"}]'
    url += '&apikey=2a67f89b'

    data = urllib.request.urlopen(url).read()
    response = json.loads(data)
    for result in response['results']:
        for item in result['items']:
            print(item['offers'])



if __name__ == "__main__":
    main()
