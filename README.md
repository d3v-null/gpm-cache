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

Usage
====

```
gpm_cache \
  --email={your google email} \
  --pwd={your google pass} \
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

`python gpm_cache.py @gpm_args.txt --pwd <your password>`

Roadmap
====

- Fix only saving to local dir problem
- Add parameter to throttle requests so that no one hits
- implement playlist-cached parameter
