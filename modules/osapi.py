#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Estoy usando server = ... para las dos funciones, buscar como mejorar eso"""

import xmlrpc.client
import gzip
import base64
import shutil
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_UA = os.getenv("OPENSUBTITLE_USER_AGENT")

server = xmlrpc.client.ServerProxy("http://api.opensubtitles.org:80/xml-rpc")


def ConnectAPI():
    # Argumentos que la API necesita, se puede cambiar a los del usuario
    user = ""  # str(input("Usuario de OpenSubtitles: ")) ??
    pwd = ""  # str(input("Contraseña: ")) ??
    ua = SECRET_UA
    # Acceder a la api y tomar el token para validar los procesos
    return server.LogIn(user, pwd, "en", ua)  # json


def DisconnectAPI(login):
    if login:
        server.LogOut(login['token'])


def SearchAPI(movie_hash, movie_size, login, lang):
    search_data = [{"moviehash": movie_hash,
                    "moviebytesize": movie_size,
                    "sublanguageid": lang}]
    return server.SearchSubtitles(login["token"], search_data)  # json


def SearchName(name, season, episode, login, lang):
    search_data = [{"query": name,
                    "season": eval("int(season) if season != \"\" else \"\""),
                    "episode": eval("int(episode) if season != \"\" else \"\""),
                    "sublanguageid": lang}]
    return server.SearchSubtitles(login["token"], search_data)  # json


def ShowSubs(data):
    if not data["data"]:
        return []  # list
    else:
        sublist = []
        for i in data["data"]:
            sublist.append(i["MovieReleaseName"])
    return sublist  # list


def DownSubs(data, sub_index, subfile_name, login):
    subfile = server.DownloadSubtitles(login["token"],
                                       [data["data"][sub_index]["IDSubtitleFile"]])
    sub_format = data["data"][sub_index]["SubFormat"]
    if subfile:
        # Save file in the computer
        with open(subfile_name+"."+sub_format, "wb") as f:
            f.write(gzip.decompress(
                base64.b64decode(subfile["data"][0]["data"])))
        return True
    else:
        return False
