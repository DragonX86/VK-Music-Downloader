# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=import-error
import contextlib
import os
import random
import string

from fuzzywuzzy import fuzz
from pathvalidate import sanitize_filename
from PyQt5.QtWidgets import QLineEdit, QMessageBox
from vk_api.audio import VkAudio
from yandex_music import Client
from yandex_music.artist.artist import Artist
from entities.album import VkAlbum
from entities.session import VkSession
from entities.song import VkSong


def get_album_description(artist_name: str, album_title: str) -> dict:
    """ TODO: generate docstring """  
    with contextlib.redirect_stderr(open(os.devnull, "w", encoding="UTF-8")):
        with contextlib.redirect_stdout(open(os.devnull, "w", encoding="UTF-8")):
            response = Client().search(sanitize_filename(artist_name))

    if response.best and response.best.type != 'artist':
        return False

    artist: Artist = response.best.result

    for album in artist.get_albums(page_size=100):
        if fuzz.WRatio(album.title, album_title) > 90:
            result = {
                'artist': artist.name,
                'title': album.title,
                'genre': album.genre,
                'year': album.year,
                'cover_url': f"https://{album.cover_uri.replace('%%', '600x600')}",
                'track_count': album.track_count
            }
            break
    else:
        return False

    return result

def validate_QLineEdit(field: QLineEdit):
    input_str = field.text()

    if input_str and not input_str.isspace():
        field.setText(input_str.strip())
        return True
    else:
        field.clear()
        return False

def print_message(message):
    msgBox = QMessageBox()

    msgBox.setWindowTitle("Сообщение о ошибке")
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(message)

    msgBox.exec()

def get_tracklist_iter(album: VkAlbum):
    vkaudio = VkAudio(VkSession().get_session())

    owner_id = album.owner_id
    album_id = album.album_id
    access_hash = album.access_hash

    for i, track in enumerate(vkaudio.get_iter(owner_id, album_id, access_hash), 1):
        yield VkSong(
            track_num=i,
            artist=album.artist,
            album=album.title,
            title=track['title'],
            cover_path=album.cover_path,
            album_path=album.album_path,
            track_code="".join(random.choice(string.ascii_lowercase) for i in range(25)),
            genre=album.genre,
            year=album.year,
            url=track['url']
        )
  