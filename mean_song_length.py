#!/usr/bin/env python3

import requests
import sys

STATUS_CODE_OK = 200

def sanitise(query):
  return query.replace(' ', '_').lower()

query = input('Enter artist name:\n')
query = sanitise(query)

try:
  response = requests.get('https://musicbrainz.org/ws/2/artist/?query={}&fmt=json'.format(query))
except requests.exceptions.ConnectionError as e:
  print(e)
  sys.exit(1)

if response.status_code is not STATUS_CODE_OK:
  print('Failed to access server')
  sys.exit(1)

response_json = response.json()
print(len(response_json['artists']))
for artist in response_json['artists']:
  print('{id} - "{name}" {disamb}'.format(
    id=artist['id'],
    name=artist['name'],
    disamb=artist['disambiguation'] if 'disambiguation' in artist else ''))

artist = response_json['artists'][0]
song_list = requests.get('https://musicbrainz.org/ws/2/artist/{artist_id}?inc=work-rels&fmt=json'.format(artist_id=artist['id']))

if song_list.status_code is not STATUS_CODE_OK:
  print('Could not retrieve songs by {}'.format(artist))
  sys.exit(1)

song_list = song_list.json()
word_counts = []
for song in song_list['relations']:
  lyrics = requests.get('https://api.lyrics.ovh/v1/{artist}/{song}'.format(
    artist=sanitise(artist['name']),
    song=sanitise(song['work']['title'])
  ))

  if lyrics.status_code is not STATUS_CODE_OK:
    continue

  word_counts.append(len(lyrics.json()['lyrics'].split()))

mean = sum(word_counts) / len(word_counts)
print('mean: {}'.format(mean))
