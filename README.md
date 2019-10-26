```

//////
//////////
/////////////
/////////////////
/////////////////////    ,,,,,,,
///////////////////..,,,,,,,,,,,,,,,,,
///////////////.,,,,,,,,,,,,,,,,,,,,,,,,,
////////////,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.
///////////,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.
/////////,,,,,,,,,,,,,,**********,,,,,,,,,,,,,,.
///////,,,,,,,,,,,,******************,,,,,,,,,,,,
///////,,,,,,,,,,**********************,,,,,,,,,,,
//////,,,,,,,,,,*************************,,,,,,,,,,
/////,,,,,,,,,,*************.    .********,,,,,,,,,,
/////,,,,,,,,,**************.    .*********,,,,,,,,,///
////,,,,,,,,,***************. *..**********,,,,,,,,,*////
////,,,,,,,,,***************. *************,,,,,,,,,*//////
////,,,,,,,,,***********.     *************,,,,,,,,,*//////
////,,,,,,,,,,*********       .************,,,,,,,,,/////
/////,,,,,,,,,*********       .***********,,,,,,,,,,/
/////,,,,,,,,,,**********.  ..**********,,,,,,,,,,
//////,,,,,,,,,,,*********************,,,,,,,,,
///////,,,,,,,,,,,,*****************,,,,,,,
////////,,,,,,,,,,,,,,***********,,,,,,
//////////,,,,,,,,,,,,,,,,,,,,,,,,,,
////////////,,,,,,,,,,,,,,,,,,,,,
//////////////,,,,,,,,,,,,,,,
/////////////////,,,,,,,,           ______ ___    ______ __  __ ______
/////////////////////              / ____//   |  / ____// / / // ____/
//////////////////                / /    / /| | / /    / /_/ // __/
//////////////                   / /___ / ___ |/ /___ / __  // /___
///////////                      \____//_/  |_|\____//_/ /_//_____/
////////

```

gpm-cache
===
[![Build Status](https://travis-ci.org/derwentx/gpm-cache.svg?branch=master)](https://travis-ci.org/derwentx/gpm-cache)
[![Maintainability](https://api.codeclimate.com/v1/badges/f28cbc664d9193b330b3/maintainability)](https://codeclimate.com/github/derwentx/gpm-cache/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/f28cbc664d9193b330b3/test_coverage)](https://codeclimate.com/github/derwentx/gpm-cache/test_coverage)


An innocuous little script that caches information about a GPM playlist using
[gmusicapi](https://github.com/simon-weber/gmusicapi)

Please use this script responsibly. Do not use this script to violate the terms
of your Google Play account, you might get in to trouble and that would be bad! `:O`

Installation
====

Install from GitHub

```sh
pip install -r requirements.txt --user
python setup.py develop --user
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
python -m gpm_cache.core \
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
--device-id
ABC123
```

and then you only have to type

`python -m gpm_cache.core @gpm_args.txt`

Roadmap
====

- [x] Ask for creds every time
- [x] [Get 2FA working](https://github.com/derwentx/gpm-cache/issues/1)
- [ ] Fix only saving to local dir problem
- [ ] implement playlist-cached parameter
