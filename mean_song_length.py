#!/usr/bin/env python3

import requests
import sys


STATUS_CODE_OK = 200

ARTIST_ENDPOINT = 'https://musicbrainz.org/ws/2/artist/'
LYRIC_ENDPOINT = 'https://api.lyrics.ovh/v1/'


def sanitise(query):
  return query.replace(' ', '_').lower()


query = input('Enter artist name:\n')
query = sanitise(query)

artist_search = requests.get('{endpoint}?query={query}&fmt=json'.format(
  endpoint=ARTIST_ENDPOINT,
  query=query
))

if artist_search.status_code is not STATUS_CODE_OK:
  print('Failed to access Musicbrainz server')
  sys.exit(1)

artist_search = artist_search.json()
# for artist in artist_search['artists']:
#   print('"{name}" {disamb}'.format(
#     name=artist['name'],
#     disamb=artist['disambiguation'] if 'disambiguation' in artist else ''
#   ))

artist = artist_search['artists'][0]
song_list = requests.get('{endpoint}{artist_id}?inc=work-rels&fmt=json'.format(
  endpoint=ARTIST_ENDPOINT,
  artist_id=artist['id']
))

if song_list.status_code is not STATUS_CODE_OK:
  print('Could not retrieve songs from Musicbrainz')
  sys.exit(1)

song_list = song_list.json()
word_counts = []
for song in song_list['relations']:
  lyrics = requests.get('{endpoint}{artist}/{song}'.format(
    endpoint=LYRIC_ENDPOINT,
    artist=sanitise(artist['name']),
    song=sanitise(song['work']['title'])
  ))

  if lyrics.status_code is not STATUS_CODE_OK:
    continue

  word_counts.append(len(lyrics.json()['lyrics'].split()))

mean = sum(word_counts) / len(word_counts)
print('\nmean: {0:.2f}'.format(mean))
