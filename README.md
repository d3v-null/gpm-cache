```



``
`:++++/:.
/ooooooo++/-`
+ooooooooooo++:.
+oooooooooooooo++/-`
+oooooooooooooooooo+/:.
ooooooooooooooooooooo++/-..----------..```
ooooooooooooooooo++/:----------------------.``
ooooooooooooooo+::----------------------------.`
oooooooooooo+/:----------------------------------.`
ooooooooooo/:--------------------------------------.`
ooooooooo+:-------------::://////////:::-------------`
oooooooo+:-----------:://////////////////:------------.
ooooooo+-----------:///////////////////////::----------.
oooooo+:----------///////////////////////////:----------.
oooooo:---------:///////////////`````-+///////:----------.
ooooo+----------////////////////     .+////////:----------/:.`
ooooo:---------://////////////// `////+/////////:---------+oo+/-`
ooooo:---------///////////////// `+++///////////:---------/ooooo+-
ooooo----------///////////////// `++/////////////---------/ooooooo`
ooooo:---------////////////-```` `++////////////:-------/oooooo:
ooooo:---------://////////`      `++////////////---------o.
ooooo+----------//////////`      .++////////////--------`
oooooo:---------://////////-```.-+/////////////------`
oooooo+:---------:////////////////////////////----.`
ooooooo+-----------:////////////////////////---.``
oooooooo+:-----------:////////////////////---.`
ooooooooo+:--------------:////////////----``
ooooooooooo/:--------------------------.`
ooooooooooooo/:------------------:--.`                       __
ooooooooooooooo+/---------------.`          _________ ______/ /_  ___
oooooooooooooooooo+/------:--.`            / ___/ __ `/ ___/ __ \/ _ \
oooooooooooooooooooooo+/:.`               / /__/ /_/ / /__/ / / /  __/
oooooooooooooooooooo+/-`                  \___/\__,_/\___/_/ /_/\___/
ooooooooooooooooo+:.
oooooooooooooo/-`
+ooooooooo+:.
`+ooooo/-`
`..`



```

gpm-cache
===
An innocuous little script that caches information about a GPM playlist using
[gmusicapi](https://github.com/simon-weber/gmusicapi)

Please use this script responsibly. Do not use this script to violate the terms
of your Google Play account, you might get in to trouble and that would be bad! `:O`

Installation
====

Install from GitHub

```sh
sudo -H pip install -r requirements.txt
python setup.py install develop
```

Testing
====

Test in your environment
```bash
python setup.py test
```

Use tox to run tests on multiple python versions
```bash
tox
```

Usage
====

```
gpm_cache \
  --email={your google email} \
  --device-id 'XXXXXXXXXXXXXXXX' \
  --cache-location '~/Music/gpm-download/' \
  --playlist={your GPM playlist} \
  --playlist-cached={playlist to move successfully cached items}
  --rate-limit={rate limit (requests per sec)}
```

Or, to save yourself typing these arguments multiple times, you can write a config
file e.g. `gpm_args.txt` like this:
```
    --email
    your@email.com
    --playlist
    Your Playlist Name
    --cache-location
    ~/your-cache-location/
    --debug-level
    info
```

and then you only have to type

`gpm_cache @gpm_args.txt`

Roadmap
====

- [x] Ask for creds every time
- [ ] Fix only saving to local dir problem
- [ ] implement playlist-cached parameter
