#!/usr/bin/env python
"""
Created by Megha Nagabhushan on 07/04/2017
"""

import json
import urllib


def main(query):
    api_key = 'your--API--Key'
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
    'query': query,
    'limit': 10,
    'indent': True,
    'key': api_key,
    'prefix': True,
    'types': 'Person'
    }

    url = service_url + '?' + urllib.urlencode(params)  # TODO: use requests
    response = json.loads(urllib.urlopen(url).read())

    # Parsing the response  TODO: log all responses
    print('Displaying results...' + ' (limit: ' + str(params['limit']) + ')\n')
    for element in response['itemListElement']:
        try:
            types = str(", ".join([n for n in element['result']['@type']]))
        except KeyError:
            types = "N/A"

        try:
            desc = str(element['result']['description'])
        except KeyError:
            desc = "N/A"

        try:
            detail_desc = str(element['result']['detailedDescription']['articleBody'])[0:100] + '...'
        except KeyError:
            detail_desc = "N/A"

        try:
            mid = str(element['result']['@id'])
        except KeyError:
            mid = "N/A"

        try:
            url = str(element['result']['url'])
        except KeyError:
            url = "N/A"

        try:
            score = str(element['resultScore'])
        except KeyError:
            score = "N/A"

        print(element['result']['name'] \
                + '\n' + ' - entity_types: ' + types \
                + '\n' + ' - description: ' + desc \
                + '\n' + ' - detailed_description: ' + detail_desc \
                + '\n' + ' - identifier: ' + mid \
                + '\n' + ' - url: ' + url \
                + '\n' + ' - resultScore: ' + score \
                + '\n')


if __name__ == '__main__':
    var = raw_input("Please enter your search query: ")
    main(var)
