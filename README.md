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
                 [-w <week number> [<week number> ...]]                                                                                         
                 [-f [<configuration file>]] [-r PROFILE] [-d DESTDIR]                                                                          
                 [-i | -g]                                                                                                                      
                 [<dest_dir deprecated>]                                                                                                        
                                                                                                                                                
Make courses from EdX powered courses available offline.                                                                                        
                                                                                                                                                
positional arguments:                                                                                                                           
  <dest_dir (deprecated)>                                                                                                                       
                        destination directory; deprecated, use --destdir                                                                        
                        option)                                                                                                                 
                                                                                                                                                
optional arguments:                                                                                                                             
  -h, --help            show this help message and exit                                                                                         
  -u USERNAME, --username USERNAME                                                                                                              
                        username (if omitted search in profile file, then                                                                       
                        .netrc used)                                                                                                            
  -p PASSWORD, --password PASSWORD                                                                                                              
                        users password                                                                                                          
  -c <course name> [<course name> ...], --courses <course name> [<course name> ...]                                                             
                        one or more course names (better use course id from                                                                     
                        the url e.g. "M101" for 10gen or "CS188.1x" for EdX )                                                                   
  -w <week number> [<week number> ...], --weeks <week number> [<week number> ...]                                                               
                        one or more weeks; -c must be present and specify only                                                                  
                        one course                                                                                                              
  -f [<configuration file>], --config-file [<configuration file>]                                                                               
                        configuration file to use                                                                                               
  -r PROFILE, --profile PROFILE                                                                                                                 
                        download profile ("10gen", "edx" etc...), must present                                                                  
                        as a section in the configuration file                                                                                  
  -d DESTDIR, --destdir DESTDIR                                                                                                                 
                        destination directory for downloaded content                                                                            
  -i, --interactive     run in interactive mode; cannot use with --gui                                                                          
  -g, --gui             show GUI menu to choose course(s)/week(s) for                                                                           
                        download; cannot use with --interactive 
```

Please note that `--gui` and `-w` options are not implemented yet.
Also positional argument `dest_dir` will be removed in future version.
You can still define configuration in `config.py` but it will be removed later or sooner so switch to using `-f` and `-r` options ASAP.
Sample file config.cfg contains 10gen and edx profiles for 10gen.com and edx.org educational sites. 
No quotes needed while defining EMAIL and PASSWORD in cgf file.

####Examples:
Download all open cources from EdX to directory /home/edu/edx-moocs:
```
python edx_dl.py -f config.cfg -r edx -d /home/edu/edx-moocs
```

Download only M101J (Mongo for Java Developers) from 10gen and manually confirm weeks/chapters to download:
```
python edx_dl.py -f config.cfg -r 10gen -c M101J -i
```
