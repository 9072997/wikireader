#! /usr/bin/env python
# -*- coding: utf-8 -*-
# COPYRIGHT: Openmoko Inc. 2009
# LICENSE: GPL Version 3 or later
# DESCRIPTION: Article Parser
# AUTHORS: Sean Moss-Pultz <sean@openmoko.com>
#          Christopher Hall <hsw@openmoko.com>

import os, sys, traceback
import re
import subprocess
import time
import getopt
import os.path
import sqlite3
import PrintLog
from types import *

verbose = False


PARSER_COMMAND = '(cd mediawiki-offline && php wr_parser_sa.php -)'

# Regular expressions for parsing the XML
subs = [
    (re.compile(r'\s*(==\s*External\s+links\s*==.*)$', re.IGNORECASE + re.DOTALL), ''),

    (re.compile(r'\s*(<|&lt;)gallery(>|&gt;).*?(<|&lt;)/gallery(>|&gt;)', re.IGNORECASE + re.DOTALL), ''),

    (re.compile(r'((<|&lt;)ref\s+name.*?/(>|&gt;))', re.IGNORECASE), ''),

    (re.compile(r'((<|&lt;)!--.*?--(>|&gt;)|(<|&lt;)ref.*?(<|&lt;)/ref(>|&gt;))', re.IGNORECASE + re.DOTALL), ''),

    (re.compile(r'(<|&lt;)br[\s"a-zA-Z0-9=]*/?(>|&gt;)', re.IGNORECASE), '\n'),

    (re.compile(r'\[\[(file|image):.*$', re.IGNORECASE + re.MULTILINE), ''),

    (re.compile(r'\[\[\w\w:(\[\[[^\]\[]*\]\]|[^\]\[])*\]\]', re.IGNORECASE), ''),

    # Wikipedia's installed Parser extension tags
    # <categorytree>, <charinsert>, <hiero>, <imagemap>, <inputbox>, <poem>,
    # <pre>, <ref>, <references>, <source>, <syntaxhighlight> and <timeline>
    # All referenced using special characters
    # Ex: <timeline> --> &lt;timeline&gt;
    # For now, we're only going to remove <timeline>
    (re.compile(r'\s*(<|&lt;)timeline(>|&gt;).*?(<|&lt;)/timeline(>|&gt;)', re.IGNORECASE + re.DOTALL), ''),
    (re.compile(r'\s*(<|&lt;)imagemap(>|&gt;).*?(<|&lt;)/imagemap(>|&gt;)', re.IGNORECASE + re.DOTALL), ''),
    (re.compile(r'(<|&lt;)references[\s"a-zA-Z0-9=]*/?(>|&gt;)', re.IGNORECASE), ''),

    (re.compile(r'&lt;div\s+style=&quot;clear:\s+both;&quot;&gt;\s*&lt;/div&gt;', re.IGNORECASE), ''),

    # remove unwanted tags
    (re.compile(r'(<|&lt;)/?(poem|source|pre)(>|&gt;)', re.IGNORECASE), ''),

    # convert &lt;tag&gt; to <tag>
    (re.compile(r'&lt;(/?)(math|nowiki|table|sub|sup|small)&gt;', re.IGNORECASE), r'<\1\2>'),

    # fix entities
    (re.compile(r'&amp;([a-zA-Z]{2,8});', re.IGNORECASE), r'&\1;'),

    # change % so php: wr_parser_sa does not convert them
    (re.compile(r'%', re.IGNORECASE), r'%25'),
]


def usage(message):
    if None != message:
        print 'error:', message
    print 'usage: %s <options> {xml-file...}' % os.path.basename(__file__)
    print '       --help                  This message'
    print '       --verbose               Enable verbose output'
    print '       --xhtml=file            XHTML output [all_articles.html]'
    print '       --start=n               First artcle to process [1] (1k => 1000)'
    print '       --count=n               Number of artcles to process [all] (1k => 1000)'
    print '       --article-offsets=file  Article file offsets database input [offsets.db]'
    print '       --templates=file        Database for templates [templates.db]'
    print '       --parse-workdir=dir     Work directory for the PHP parser [/tmp]'
    print '       --just-cat              Replace php parser be "cat" for debugging'
    print '       --no-output             Do not run any parsing'
    exit(1)

def main():
    global verbose
    global PARSER_COMMAND
    global total_articles

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hvx:s:c:o:jnw:',
                                   ['help', 'verbose', 'xhtml=',
                                    'start=', 'count=',
                                    'article-offsets=',
                                    'templates=',
                                    'just-cat',
                                    'no-output',
                                    'parser-workdir=',
                                    ])
    except getopt.GetoptError, err:
        usage(err)

    verbose = False
    out_name = 'all_articles.html'
    off_name = 'offsets.db'
    parser_workdir='/tmp'
    start_article = 1
    article_count = 'all'
    failed_articles = 0
    do_output = True
    template_name = 'templates.db'

    for opt, arg in opts:
        if opt in ('-v', '--verbose'):
            verbose = True
        elif opt in ('-h', '--help'):
            usage(None)
        elif opt in ('-x', '--xhtml'):
            out_name = arg
        elif opt in ('-o', '--article-offsets'):
            off_name = arg
        elif opt in ('-t', '--templates'):
            template_name = arg
        elif opt in ('-w', '--parser-workdir'):
            parser_workdir = arg
        elif opt in ('-j', '--just-cat'):
            PARSER_COMMAND = 'cat'
        elif opt in ('-n', '--no-output'):
            do_output = False
        elif opt in ('-s', '--start'):
            if arg[-1] == 'k':
                arg = arg[:-1] + '000'
            try:
                start_article = int(arg)
            except ValueError:
                usage('%s=%s" is not numeric' % (opt, arg))
            if start_article < 1:
                usage('%s=%s" must be >= 1' % (opt, arg))
        elif opt in ('-c', '--count'):
            if arg[-1] == 'k':
                arg = arg[:-1] + '000'
            if arg != 'all':
                try:
                    article_count = int(arg)
                except ValueError:
                    usage('%s=%s" is not numeric' % (opt, arg))
            if article_count <= 0:
                usage('%s=%s" must be > zero' % (opt, arg))
        else:
            usage('unhandled option: ' + opt)

    if not os.path.isdir(parser_workdir):
        usage('workdir: %s does not exist' % parser_workdir)

    # pass parameters to the PHP parser
    os.environ['WORKDIR'] = parser_workdir
    os.environ['TEMPLATE_DB'] = template_name

    offset_db = sqlite3.connect(off_name)
    offset_db.execute('pragma synchronous = 0')
    offset_db.execute('pragma temp_store = 2')
    offset_db.execute('pragma read_uncommitted = true')
    offset_db.execute('pragma cache_size = 20000000')
    offset_db.execute('pragma default_cache_size = 20000000')
    offset_db.execute('pragma journal_mode = off')

    offset_cursor = offset_db.cursor()

    if do_output:
        background_process = PARSER_COMMAND + ' > ' + out_name
    else:
        background_process = None

    # process all required articles
    out_base_name = os.path.basename(out_name) # for logging messages
    current_file_id = None
    input_file = None
    process_id = None
    total_articles = 0
    start_time = time.time()
    while article_count == 'all' or article_count != 0:
        offset_cursor.execute('select file_id, title, seek, length from offsets where article_number = ? limit 1',
                              (start_article,))
        row = offset_cursor.fetchone()
        if None == row:
            break
        (file_id, title, seek, length) = row

        if file_id != current_file_id:
            current_file_id = file_id
            if input_file:
                input_file.close()
            offset_cursor.execute('select filename from files where file_id = ? limit 1', (file_id,))
            filename = offset_cursor.fetchone()[0]
            input_file = open(filename, 'r')
            if not input_file:
                PrintlogLog.message('Failed to open: %s' % filename)
                current_file_id = None
                continue
            if verbose:
                PrintLog.message('Opened: %s' % filename)

        try:
            input_file.seek(seek)
        except Exception, e:
            PrintLog.message('seek failed: e=%s  seek=%d  f=%s name=%s' % (str(e), seek, filename))
            sys.exit(1)

        # restart the background process if it fails to try to record all failing articles
        if None != background_process and None == process_id:
            process_id = subprocess.Popen(background_process, shell=True, stdin=subprocess.PIPE)

        try:
            process_article_text(current_file_id, title.encode('utf-8'),
                                 input_file.read(length), process_id.stdin)
        except Exception, e:
            failed_articles += 1
            # extract from log by: grep '^!' log-file
            PrintLog.message('!Process failed, file: %s article(%d): %s because: %s'
                             % (filename, total_articles, title, str(e)))
            trace = sys.exc_info()
            if None != trace:
                traceback.print_tb(trace[2])
            process_id.stdin.close()
            process_id.wait()
            process_id = None

        if article_count != 'all':
            article_count -= 1
        total_articles += 1
        start_article += 1
        if not verbose and total_articles % 1000 == 0:
            if 0 != failed_articles:
                failed_message = 'Failed: %d' % failed_articles
            else:
                failed_message = ''
            now_time = time.time()
            PrintLog.message('Parse[%s]: %7.2fs %10d  %s' %
                             (out_base_name, now_time - start_time,
                              total_articles, failed_message))
            start_time = now_time

    # close files
    if input_file:
        input_file.close()

    # wait for background process to finish
    if process_id:
        process_id.stdin.close()
        process_id.wait()

    # output some statistics
    PrintLog.message('Total:  %d' % total_articles)

    # indicate failures
    if 0 != failed_articles:
        PrintLog.message('Failed: %d' % failed_articles)
        sys.exit(1)


def process_article_text(id, title, text, newf):
    global verbose
    global subs

    if verbose:
        PrintLog.message('[PA] %s' % title)

    for e,r in subs:
        text = e.sub(r, text)

    if newf:
        newf.write('%d:' % id)
        newf.write(title[1:])  # We pad the title to force the database to import strings
        newf.write('\n__NOTOC__\n')
        newf.write(text + '\n')
        newf.write('***EOF***\n')


# run the program
if __name__ == "__main__":
    main()

