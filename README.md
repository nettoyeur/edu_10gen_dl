# EdX powered courses video downloader

This script is intended to download course videos from http://education.10gen.com
or any other site 'Powered by EdX' (including, of course, http://edx.org itself).

This script relies on [youtube-dl](https://github.com/rg3/youtube-dl/) project
to download videos.

Accepts destination path as optional parameter.

###Dependencies:

* Python 2.7
* Mechanize
* BeautifulSoup4
* Youtube\_dl

### Installation

    git clone https://github.com/nonsleepr/edu_10gen_dl.git
    cd edu_10gen_dl
    sudo pip install -r requirements.txt

Populate `config.py` with domain and credentials of site, from which you're going to download videos.

Optionally set another options in `config.py` like `writesubtitles` to enable subtitles.

### Usage:

```
usage: edx_dl.py [-h] [-u USERNAME] [-p PASSWORD]
                 [-c <course name> [<course name> ...]]
                 [-d DESTDIR] [-i]

Make courses from EdX powered courses available offline.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        username (if omitted search in profile file, then
                        .netrc used)
  -p PASSWORD, --password PASSWORD
                        users password
  -c <course name> [<course name> ...], --courses <course name> [<course name> ...]
                        one or more course names (better use course id in the
                        url e.g. "M101" for 10gen or "CS188.1x" for EdX )
  -d DESTDIR, --destdir DESTDIR
                        destination directory for downloaded content
  -i, --interactive     run in interactive mode

```
