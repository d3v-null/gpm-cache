gpm-cache
===
An innocuous little script that caches information about a GPM playlist using [gmusicapi](https://github.com/simon-weber/gmusicapi)

Please use this script responsibly. Do not use this script to violate the terms of your Google Play account, you might get in to trouble and that would be bad! `:O`

Installation
====

Install requirements

`sudo -H pip install -r requirements.txt`

Usage
====

`
python gpm-cache.py \
  --email={your google email} \
  --pwd={your google pass} \
  --playlist={your GPM playlist} \
  --playlist-cached={playlist to move successfully cached items}
  --rate-limit={rate limit (requests per sec)}
`

Roadmap
====

- Fix only saving to local dir problem
- Add parameter to throttle requests so that no one hits 
- implement playlist-cached parameter
