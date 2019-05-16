import sys
import os
from urllib.request import urlopen

try:
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3, APIC, ID3NoHeaderError
    import mutagen
    tagging = True
except ImportError:
    tagging = False
    pass

from colorama import Fore, Style

def main():
    if len(sys.argv) > 2:
        for i in range(len(sys.argv) - 1):
            if sys.argv[i] == "-d":
                if i == len(sys.argv) - 1:
                    exit("You didnt specify a URL to an artist!")
                rip_disc(sys.argv[i + 1])
            elif sys.argv[i] == "-a":
                if i == len(sys.argv) - 1:
                    exit("You didnt specify a URL to an album!")
                rip(sys.argv[i + 1])
    else:
        exit("Too few arguments!")

def rip_disc(URL):
    url_req = urlopen(URL)
    source = url_req.read().decode("utf-8")

    source = source.replace('&quot;', '"')

    artist = source.split("<title>")[1].split("</title>")[0].split(" | ")[1]

    print("Ripping albums from " + artist + "\n")

    url_sto = source.split('"page_url":"')

    album_count = len(url_sto) - 1

    for i in range(album_count):
        new_dir = URL + url_sto[i + 1].split('"')[0]
        rip(new_dir)
        print()

def rip(URL):
    url_req = urlopen(URL)
    source = url_req.read().decode("utf-8")

    d_sto = source.split('"mp3-128":"')
    music_count = len(d_sto) - 1
    n_sto = source.split('"title":"')

    data = source.split('<title>')[1].split('</title>')[0].split(" | ")

    albumart = source.split('<div id="tralbumArt">')[1].split('</div>')[0].split('<img src="')[1].split('"')[0]

    art = urlopen(albumart).read()

    #print(art)

    album = validate(data[0])
    artist = validate(data[1])

    print(album)

    dir = artist + "/" + album + "/"

    if not os.path.exists(dir):
        os.makedirs(dir)

    for i in range(music_count):
        name = n_sto[i + 2].split('"')[0]
        name = validate(name)
        print("Downloading [" + name + "]")
        download(d_sto[i + 1].split('"')[0], dir + str(i + 1) + ". " + name)
        if tagging:
            tag(dir + str(i + 1) + ". " + name, artist, album, i + 1, name, art)

def download(URL, filename):
    file = urlopen(URL)
    with open(filename + ".mp3", "wb") as output:
        output.write(file.read())
    pass

def validate(fname):
    fsto = fname
    for c in r'[]/\;,><&*:%=+@!#^()|?^':
        fsto = fsto.replace(c, '')
    return fsto

def tag(filename, artist, album, track, title, albumart):
    try:
        f = EasyID3(filename + ".mp3")
    except ID3NoHeaderError:
        f = mutagen.File(filename + ".mp3",easy=True)
        f.add_tags()
    #print(f.keys())

    f['album'] = album
    f['artist'] = artist
    f['tracknumber'] = str(track)
    f['title'] = title

    f.save()

    f = ID3(filename + ".mp3", )
    f["APIC"] = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=albumart)
    f.save(v2_version=3)
    #print(f.keys())

if __name__ == "__main__":
    sys.exit(main())