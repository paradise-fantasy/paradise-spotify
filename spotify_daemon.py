#! /usr/bin/python2

from pydbus import SessionBus
from gi.repository import GLib
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading

def on_spotify_change(mpris_object, data, som_kind_of_list):
    global current
    if (data != current):
        current = data
        payload = generate_json_object(current)
        sendMQTT(payload)

def generate_json_object(data):
    status = data['PlaybackStatus']
    albumArt = data['Metadata']['mpris:artUrl']
    artist = data['Metadata']['xesam:artist'][0]
    title = data['Metadata']['xesam:title']
    album = data['Metadata']['xesam:album']

    return {
        'status': status,
        'title': title,
        'artist': artist,
        'album': album,
        'albumArt': str(albumArt)
    }

def sendMQTT(payload):
    publish.single("paradise/api/spotify",
        json.dumps(payload),
        port=8883,
        tls={'ca_certs':"../ca.crt",'tls_version':2},
        hostname="nyx.bjornhaug.net"
    )

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("paradise/notify/spotify")

def on_message(client, userdata, msg):
    global spotify

    try:
        if (str(msg.payload) == 'play-pause'):
                spotify.PlayPause()
        elif (str(msg.payload) == 'play'):
            spotify.Play()
        elif (str(msg.payload) == 'pause'):
            spotify.Pause()
        elif (str(msg.payload) == 'next'):
            spotify.Next()
        elif (str(msg.payload) == 'previous'):
            spotify.Previous()
        elif (str(msg.payload) == 'stop'):
            spotify.stop()
    except:
        print "I alle dager. Dette gikk ikke."

def handle_threads(spotify_worker, mqtt_worker):

    spotify_thread = threading.Thread(target=spotify_worker.run)
    spotify_thread.start()
    front_end_thread = threading.Thread(target=mqtt_worker.loop_forever)
    front_end_thread.start()

def main():
    global loop
    global bus

    spotify.PropertiesChanged.connect(on_spotify_change)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set("../ca.crt")
    client.connect("nyx.bjornhaug.net", 8883, 60)

    handle_threads(loop, client)

if __name__ == "__main__":
    current = ""
    loop = GLib.MainLoop()
    bus = SessionBus()
    spotify = bus.get(
    "org.mpris.MediaPlayer2.spotify", # Bus name
    "/org/mpris/MediaPlayer2" # Object path
    )
    main()

