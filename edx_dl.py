#!/usr/bin/python
# -*- coding: utf-8 -*-

import glob
import json
import mechanize
import re
import sys
import os.path
import getpass
import netrc
import platform
import os
import argparse
from bs4 import BeautifulSoup
from math import floor
from random import random
from urllib import urlencode

from youtube_dl.FileDownloader import FileDownloader
from youtube_dl.InfoExtractors  import YoutubeIE
from youtube_dl.utils import sanitize_filename

def makeCsrf():
    t = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    e = 24
    csrftoken = list()
    for i in range(0,e):
        csrftoken.append(t[int(floor(random()*len(t)))])
    return ''.join(csrftoken)

def csrfCookie(csrftoken, domain):
    return mechanize.Cookie(version=0,
            name='csrftoken',
            value=csrftoken,
            port=None, port_specified=False,
            domain=domain,
            domain_specified=False,
            domain_initial_dot=False,
            path='/', path_specified=True,
            secure=False, expires=None,
            discard=True,
            comment=None, comment_url=None,
            rest={'HttpOnly': None}, rfc2109=False)


def get_netrc_creds(authenticator):
    """
    Read username/password from the users' netrc file. Returns None if no
    coursera credentials can be found.
    """
    # inspired by https://github.com/jplehmann/coursera
    # taken from  https://github.com/dgorissen/coursera-dl

    if platform.system() == 'Windows':
        # where could the netrc file be hiding, try a number of places
        env_vars = ["HOME","HOMEDRIVE", "HOMEPATH","USERPROFILE","SYSTEMDRIVE"]
        env_dirs = [os.environ[e] for e in env_vars if os.environ.get(e,None)]

        # also try the root/cur dirs
        env_dirs += ["C:", ""]

        # possible filenames
        file_names = [".netrc", "_netrc"]

        # all possible paths
        paths = [os.path.join(dir,fn) for dir in env_dirs for fn in file_names]
    else:
        # on *nix just put None, and the correct default will be used
        paths = [None]

    # try the paths one by one and return the first one that works
    creds = None
    for p in paths:
        try:
            auths = netrc.netrc(p).authenticators(authenticator)
            creds = (auths[0], auths[2])
            print "Credentials found in .netrc file"
            break
        except (IOError, TypeError, netrc.NetrcParseError) as e:
            pass

    return creds

class EdXBrowser(object):
    def __init__(self, config):
        self._config = config
        self._br = mechanize.Browser()
        self._cj = mechanize.LWPCookieJar()
        csrftoken = makeCsrf()
        self._cj.set_cookie(csrfCookie(csrftoken, self._config['DOMAIN']))
        self._br.set_handle_robots(False)
        self._br.set_cookiejar(self._cj)
        self._br.addheaders.append(('X-CSRFToken',csrftoken))
        self._br.addheaders.append(('Referer',base_url))
        self._logged_in = False
        self._fd = FileDownloader(self._config.get('YDL_PARAMS'))
        self._fd.add_info_extractor(YoutubeIE())

    def login(self):
        try:
            login_resp = self._br.open(base_url + login_url, urlencode({'email':self._config['EMAIL'], 'password':self._config['PASSWORD']}))
            login_state = json.loads(login_resp.read())
            self._logged_in = login_state.get('success')
            if not self._logged_in:
                print login_state.get('value')
            return self._logged_in
        except mechanize.HTTPError, e:
            sys.exit('Can\'t sign in')

    def list_courses(self):
        self.courses = []
        if self._logged_in:
            dashboard = self._br.open(base_url + dashboard_url)
            dashboard_soup = BeautifulSoup(dashboard.read())
            my_courses = dashboard_soup.findAll('article', 'my-course')
            i = 0
            for my_course in my_courses:
                course_url = my_course.a['href']
                course_name = my_course.h3.text
                
                if self._config['interactive_mode']:
                    launch_download_msg = 'Download the course [%s] from %s? (y/n) ' % (course_name, course_url)
                    launch_download = raw_input(launch_download_msg)
                    if (launch_download.lower() == "n"):
                        continue

                i += 1
                courseware_url = re.sub(r'\/info$','/courseware',course_url)
                self.courses.append({'name':course_name, 'url':courseware_url})
                print '[%02i] %s' % (i, course_name)

    def list_chapters(self, course_i):
        self.paragraphs = []
        if course_i < len(self.courses) and course_i >= 0:
            print "Getting chapters..."
            course = self.courses[course_i]
            course_name = course['name']
            courseware = self._br.open(base_url+course['url'])
            courseware_soup = BeautifulSoup(courseware.read())
            chapters = courseware_soup.findAll('div','chapter')
            i = 0
            for chapter in chapters:
                chapter_name = chapter.find('h3').find('a').text

                if self._config['interactive_mode']:
                    launch_download_msg = 'Download the chapter [%s - %s]? (y/n) ' % (course_name, chapter_name)
                    launch_download = raw_input(launch_download_msg)
                    if (launch_download.lower() == "n"):
                        continue
                
                i += 1
                print '\t[%02i] %s' % (i, chapter_name)
                paragraphs = chapter.find('ul').findAll('li')
                j = 0
                for paragraph in paragraphs:
                    j += 1
                    par_name = paragraph.p.text
                    par_url = paragraph.a['href']
                    self.paragraphs.append((course_name, i, j, chapter_name, par_name, par_url))
                    print '\t\t[%02i.%02i] %s' % (i, j, par_name)

    def download(self):
        print "\n-----------------------\nStart downloading\n-----------------------\n"
        for (course_name, i, j, chapter_name, par_name, url) in self.paragraphs:
            #nametmpl = sanitize_filename(course_name) + '/' \
            #         + sanitize_filename(chapter_name) + '/' \
            #         + '%02i.%02i.*' % (i,j)
            #fn = glob.glob(DIRECTORY + nametmpl)
            nametmpl = os.path.join(self._config['directory'],
                                    sanitize_filename(course_name, replace_space_with_underscore),
                                    sanitize_filename(chapter_name, replace_space_with_underscore),
                                    '%02i.%02i.*' % (i,j))
            fn = glob.glob(nametmpl)
            
            if fn:
                print "Processing of %s skipped" % nametmpl
                continue
            print "Processing %s..." % nametmpl
            par = self._br.open(base_url + url)
            par_soup = BeautifulSoup(par.read())
            contents = par_soup.findAll('div','seq_contents')
            k = 0
            for content in contents:
                #print "Content: %s" % content
                content_soup = BeautifulSoup(content.text)
                try:
                    video_type = content_soup.h2.text.strip()
                    video_stream = content_soup.find('div','video')['data-streams']
                    video_id = video_stream.split(':')[1]
                    video_url = youtube_url + video_id
                    k += 1
                    print '[%02i.%02i.%02i] %s (%s)' % (i, j, k, par_name, video_type)
                    #f.writelines(video_url+'\n')
                    #outtmpl = DIRECTORY + sanitize_filename(course_name) + '/' \
                    #        + sanitize_filename(chapter_name) + '/' \
                    #        + '%02i.%02i.%02i ' % (i,j,k) \
                    #        + sanitize_filename('%s (%s)' % (par_name, video_type)) + '.%(ext)s'
                    outtmpl = os.path.join(self._config['directory'],
                        sanitize_filename(course_name, replace_space_with_underscore),
                        sanitize_filename(chapter_name, replace_space_with_underscore),
                        '%02i.%02i.%02i ' % (i,j,k) + \
                        sanitize_filename('%s (%s)' % (par_name, video_type)) + '.%(ext)s', replace_space_with_underscore)
                    self._fd.params['outtmpl'] = outtmpl
                    self._fd.download([video_url])
                except Exception as e:
                    #print "Error: %s" % e
                    pass

replace_space_with_underscore = True
youtube_url = 'http://www.youtube.com/watch?v='

base_url = None
login_url = '/login'
dashboard_url = '/dashboard'

def setup_urls(config):
    global base_url, login_url, dashboard_url
    domain = config['DOMAIN']
    base_url = 'https://' + domain
    # Dirty hack for differences in 10gen and edX implementation
    if 'edx' in domain.split('.'):
        login_url = '/login_ajax'
    else:
        login_url = '/login'
    dashboard_url = '/dashboard'

def read_config(profile):
    """if profile:
        #exec "import %s" % args.profile
        cfg_parser = ConfigParser.ConfigParser()
        if profile not in cfg_parser.sections():
            raise Exception("Profile '%s' is not defined" % profile)
    else:
    """
    import config
    cfg_dict = {}
    if hasattr(config, 'DOMAIN'):
        cfg_dict['DOMAIN'] = config.DOMAIN
    if hasattr(config, 'EMAIL'):
        cfg_dict['EMAIL'] = config.EMAIL
    if hasattr(config, 'PASSWORD'):
        cfg_dict['PASSWORD'] = config.PASSWORD
    if hasattr(config, 'YDL_PARAMS'):
        cfg_dict['YDL_PARAMS'] = config.YDL_PARAMS
    return cfg_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make courses from EdX powered courses available offline.', add_help=True)
    parser.add_argument("-u", "--username", dest='username', type=str, help='username (if omitted search in profile file, then .netrc used)')
    parser.add_argument("-p", "--password", dest='password', type=str, help='user''s password')
    parser.add_argument('-c', "--courses", dest="course_names", nargs="+", metavar='<course name>', type=str, help='one or more course names (e.g. TODO)')
    parser.add_argument('-w', "--weeks", dest="week_numbers", nargs="+", metavar='<week number>', type=str, help='one or more weeks; -c must be present and specify only one course')
    parser.add_argument('-r', "--profile", dest="profile", type=str, help='download profile ("10gen", "edx" etc...)')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', "--destdir", dest="destdir", type=str, default=".", help='destination directory for downloaded content')
    group.add_argument('dest_dir', nargs="?", metavar='<dest_dir (deprecated)>', type=str, help='destination directory; deprecated, use --destdir option)')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', "--interactive", dest="interactive_mode", help='run in interactive mode; cannot use with --gui', action="store_true")
    group.add_argument('-g', "--gui", dest="gui_mode", help='show GUI menu to choose course(s)/week(s) for download; cannot use with --interactive', action="store_true")

    #parser.add_argument("-q", dest='parser', type=str, default=CourseraDownloader.DEFAULT_PARSER,
    #                    help="the html parser to use, see http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser")
    #parser.add_argument("-x", dest='proxy', type=str, default=None, help="proxy to use, e.g., foo.bar.com:3125")
    args = parser.parse_args()
    #print args

    config = read_config(args.profile)
    # search for login credentials in .netrc file if username hasn't been provided in command-line args
    username, password = args.username, args.password
    netrc_password = None
    if not username:
        username = config.get('EMAIL', None)
    if not username:
        creds = get_netrc_creds(config['DOMAIN'])
        if creds:
            username, netrc_password = creds
        else:
            #raise Exception("No username passed and no .netrc credentials found, unable to login")
            pass
    if not username:
        username = raw_input('Enter username for %s: ' % config['DOMAIN'])
    if not password:
        password = config.get('PASSWORD', None)
    if not password:
        password = netrc_password
        # prompt the user for his password if not specified
    if not password:
        password = getpass.getpass('Enter password for %s at %s: ' % (username, config['DOMAIN']))

    config['EMAIL'] = username
    config['PASSWORD'] = password

    config['interactive_mode'] = args.interactive_mode
    config['gui_mode'] = args.gui_mode

    if args.dest_dir:
        print "Positional argument for destination directory is deprecated, please use --destdir or -d option"
        config['directory'] = args.dest_dir
    else:
        config['directory'] = args.destdir
        pass
    print 'Downloading to ''%s'' directory' % config['directory']

    setup_urls(config)
    edxb = EdXBrowser(config)
    edxb.login()
    print 'Found the following courses:'
    edxb.list_courses()
    if edxb.courses:
        print "Processing..."
    else:
        print "No courses selected, nothing to download"
    for c in range(len(edxb.courses)):
        print 'Course: ' + str(edxb.courses[c])
        print 'Chapters:'
        edxb.list_chapters(c)
        edxb.download()
