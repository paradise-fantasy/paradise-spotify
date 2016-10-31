import paho.mqtt.publish as publish
import subprocess, json
from time import sleep

def procHandler(cmd):
    proc = subprocess.Popen('DISPLAY=:0 playerctl ' + cmd, stdout=subprocess.PIPE, shell=True)
    (stat, error) = proc.communicate()
    return stat.replace("\n", '')

def sendMQTT(payload):
    publish.single("paradise/api/spotify", json.dumps(payload), port=8883, tls={'ca_certs':"/home/paradise/ca.crt",'tls_version':2}, hostname="nyx.bjornhaug.net")

def getInfo():
    status = procHandler('status')
    albumArt = procHandler('metadata mpris:artUrl')
    artist = procHandler('metadata xesam:artist')
    title = procHandler('metadata xesam:title')
    album = procHandler('metadata xesam:album')
    return {
        'status': status,
        'title': title,
        'artist': artist,
        'album': album,
        'albumArt': str(albumArt)
    }

def main():
    lastInfo = getInfo()

    while True:
        sleep(0.5)
        info = getInfo()
        if (json.dumps(info) != json.dumps(lastInfo)):
            sendMQTT(info)
            lastInfo = info

main()
