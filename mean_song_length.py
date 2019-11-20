#!/usr/bin/env python3

import argparse
import requests
import sys


STATUS_CODE_OK = 200

ARTIST_ENDPOINT = 'https://musicbrainz.org/ws/2/artist/'
LYRIC_ENDPOINT = 'https://api.lyrics.ovh/v1/'


def main():
  artist = sanitise(parse_args().artist)

  artist_search = requests.get('{endpoint}?query={query}&fmt=json'.format(
    endpoint=ARTIST_ENDPOINT,
    query=artist
  ))

  if artist_search.status_code is not STATUS_CODE_OK:
    print('Failed to access Musicbrainz server')
    sys.exit(1)

  artist_search = artist_search.json()
  results = ['{}) "{}" {}'.format(n, artist['name'], artist['disambiguation'] if 'disambiguation' in artist else '')
             for n, artist
             in enumerate(artist_search['artists'])]
  results = '\n'.join(results)
  print(results)

  while True:
    artist_choice = input('\nSelect artist by number: ')

    try:
      artist = artist_search['artists'][int(artist_choice)]
    except Exception:
      continue

    break

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

  try:
    mean = sum(word_counts) / len(word_counts)
    print('\nmean: {0:.2f}'.format(mean))
  except ZeroDivisionError:
    print('\nNo lyrics found for {}'.format(artist['name']))


def parse_args():
  parser = argparse.ArgumentParser(description='Given an artist, return the mean number of words in their songs.')

  parser.add_argument('artist', type=str,
                      help='artist name')

  return parser.parse_args()


def sanitise(query):
  return query.replace(' ', '_').lower()


main()
