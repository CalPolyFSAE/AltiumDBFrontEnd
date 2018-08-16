import json
import urllib.request
import urllib.parse


def main():
    url = 'https://octopart.com/api/v3/parts/search?'
    args = [
        ('q', 'SN74S74N'),
        ('offers.seller.name', 'Digi-Key'),
        ('sortby', 'part["offers"][0]["prices"]["USD"][1][1]')
    ]
    url += '&' + urllib.parse.urlencode(args)
    url += '&apikey=2a67f89b'

    print(url)
    data = urllib.request.urlopen(url).read()
    response = json.loads(data)
    print(response['hits'])

    for result in response['results']:
        part = result['item']
        print(part['offers'][0]['prices']['USD'][1][1])
        print(part['brand']['name'],part['mpn'])



if __name__ == "__main__":
    main()
