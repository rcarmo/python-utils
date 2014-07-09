#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image utilities

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

from operator import itemgetter

def linear_partition(seq, k):
    if k <= 0:
        return []
    n = len(seq) - 1
    if k > n:
        return map(lambda x: [x], seq)
    table, solution = linear_partition_table(seq, k)
    k, ans = k-2, []
    while k >= 0:
        ans = [[seq[i] for i in xrange(solution[n-1][k]+1, n+1)]] + ans
        n, k = solution[n-1][k], k-1
    return [[seq[i] for i in xrange(0, n+1)]] + ans


def linear_partition_table(seq, k):
    n = len(seq)
    table = [[0] * k for x in xrange(n)]
    solution = [[0] * (k-1) for x in xrange(n-1)]
    for i in xrange(n):
        table[i][0] = seq[i] + (table[i-1][0] if i else 0)
    for j in xrange(k):
        table[0][j] = seq[0]
    for i in xrange(1, n):
        for j in xrange(1, k):
            table[i][j], solution[i-1][j-1] = min(
                ((max(table[x][j-1], table[i][0]-table[x][0]), x) for x in xrange(i)),
                key=itemgetter(0))
    return (table, solution)


def get_info(data):
    """Parses a small buffer and attempts to return basic image metadata"""
    
    data = str(data)
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    # handle GIFs
    if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack("<HH", data[6:10])
        width = int(w)
        height = int(h)

    # See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
          and (data[12:16] == 'IHDR')):
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)

    # Maybe this is for an older PNG version.
    elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
        # Check to see if we have the right content type
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[8:16])
        width = int(w)
        height = int(h)

    # Check for a JPEG
    elif (size >= 4):                                                          
        jpeg = StringIO.StringIO(data)                                         
        b = jpeg.read(4)                                                       
        if b.startswith('\xff\xd8\xff\xe0'):                                   
            content_type = 'image/jpeg'                                        
            bs = jpeg.tell()                                                   
            b = jpeg.read(2)                                                   
            bl = (ord(b[0]) << 8) + ord(b[1])                                  
            b = jpeg.read(4)                                                   
            if b.startswith("JFIF"):                                           
                bs += bl                                                       
                while(bs < len(data)):                                         
                    jpeg.seek(bs)                                              
                    b = jpeg.read(4)                                           
                    bl = (ord(b[2]) << 8) + ord(b[3])                          
                    if bl >= 7 and b[0] == '\xff' and b[1] == '\xc0':          
                        jpeg.read(1)                                           
                        b = jpeg.read(4)                                       
                        height = (ord(b[0]) << 8) + ord(b[1])                  
                        width = (ord(b[2]) << 8) + ord(b[3])                   
                        break                                                  
                    bs = bs + bl + 2      
    return width, height, content_type  
