#!/usr/bin/python
"""
 A simple code to convert a .blib file to something easy to parse
 and display on the target device.

 Copyright (C) 2008, 2009 Holger Hans Peter Freyther <zecke@openmoko.org>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import fontmap
import struct
import textrun


def usage():
    print "Wikipedia simple text coding"
    print "Usage: %s <render_text.blib> <fontmap.map>" % sys.argv[0]
    print "\t<render_text.blib> Generated by the patched GtkLauncher"
    print "\t<fontmap.map> Generated by the get_font_file.py"
    print "smplpedi.cde (Simple Wikipedia Code) is the output"
    sys.exit(1)


if len(sys.argv) < 3:
    usage()
    

glyphs = textrun.load(open(sys.argv[1]))
text_runs = textrun.generate_text_runs(glyphs, 240)
text_runs.sort(textrun.TextRun.cmp)
fonts  = fontmap.load(sys.argv[2])

# Now convert it...
# Font Number
# Number of 3-Tuples
# X
# Y
# Glyph
output = open("smplpedi.cde", "w")

for run in text_runs:
    output.write(struct.pack("<II", fonts[run.font], len(run.glyphs)))
    for glyph in run.glyphs:
        output.write(struct.pack("<III", glyph['x'], glyph['y'], int(glyph['glyph'])))

print "Done. Have fun!"
