#!/usr/bin/env python3

import sys
import os
import time
from numpy import int8
from bitstream import BitStream

# Shannon-Fano Coding for Lossless Data Compression

# =============================================================================
# The algorithm
# =============================================================================

# TODO comment
#
# ::param:: iA, iB - index interval
#
def shannon_fano_encoder(iA, iB):
    global tupleList
    size = iB - iA + 1
    if size > 1:
        # Divide the list into 2 groups.
        # Top group will get 0, bottom 1 as the new encoding bit.
        mid = 0
        localFrequency = 0
        for i in range(iA, iB + 1):
            localFrequency += tupleList[i][0]
        equilibrium = localFrequency/2
        currentFrequency = 0
        top = True
        for i in range(iA, iB + 1):
            tup = tupleList[i]
            if top: # top group
                tupleList[i] = (tup[0], tup[1], tup[2] + '0')
            else: # bottom group
                tupleList[i] = (tup[0], tup[1], tup[2] + '1')
            if top:
                currentFrequency += tup[0]
                nextFrequency = currentFrequency + tupleList[i+1][0]
                if nextFrequency > equilibrium:
                    top = False
                    mid = i+1
        # do recursive calls for both groups
        shannon_fano_encoder(iA, mid - 1)
        shannon_fano_encoder(mid, iB)

# ===========================================
# Utility functions
# ===========================================

# check global variable 'bitStream' (string), if it's more than
# 8 characters, write chars to a file in groups of 8 (byte),
# until 'bitStream' is less than 8 chars. 'bitStream' variable
# is always less than 8 after the execution of 'byteWriter'
#
# ::param:: bitStr - a string to add to 'bitStream' at the
#           start of the function
# ::param:: outputFile
#
def byteWriter(bitStr, outputFile):
    global bitStream
    bitStream += bitStr
    while len(bitStream) > 8: # write byte(s) if there are more then 8 bits
        byteStr = bitStream[:8]
        bitStream = bitStream[8:]
        outputFile.write(bytes([int(byteStr, 2)]))

# TODO comment
#
# ::param:: n - number of bits to read
#
def bitReader(n):
    global byteArr
    global bitPosition
    bitStr = ''
    for i in range(n):
        bitPosInByte = 7 - (bitPosition % 8)
        bytePosition = int(bitPosition / 8)
        if bytePosition >= len(byteArr) - 2:
            return ''
        byteVal = byteArr[bytePosition]
        bitVal = int(byteVal / (2 ** bitPosInByte)) % 2
        bitStr += str(bitVal)
        bitPosition += 1 # prepare to read the next bit
    return bitStr

# =============================================================================
# File input
# =============================================================================

if len(sys.argv) < 4:
    sys.exit('Usage: ShannonFano.py [e|d] '
          '[path]InputFileName [path]OutputFileName parameter')

mode = sys.argv[1] # encoding/decoding

if mode not in ['e', 'd']:
    sys.exit("ERROR: Mode is not one of 'e' (encoding) or 'd' (decoding)")

inputFile = sys.argv[2]
outputFile = sys.argv[3]

if os.stat(inputFile).st_size == 0:
    sys.exit('ERROR: The provided file is empty!')

fileSize = os.path.getsize(inputFile)
fi = open(inputFile, 'rb')

# just an array of bytes read
byteArr = bytearray(fi.read(fileSize))

fi.close()

# file size in bytes
fileSize = len(byteArr)

if fileSize < 1000:
    print('Input file size {} B\n'.format(fileSize))
elif fileSize < 10**6:
    print('Input file size {} KB\n'.format(fileSize/10**3))
else:
    print('Input file size {} MB\n'.format(fileSize/10**6))

start_time = time.time()
mid_time = time.time()

# =============================================================================
# Encoding
# =============================================================================

DEBUG = False

def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

# example:
#   mode = 'e'
#   inputFile = './input.txt'
#   outputFile = './encoded.bin'

if mode == 'e':
    parameter = int(sys.argv[4])

    freqList = [0] * 2**parameter
    byteStr = ''
    for byte in byteArr:
        bitStrem = BitStream()
        bitStrem.write(byte, int8)
        byteStr += str(bitStrem)
        while len(byteStr) >= parameter:
            word = byteStr[:parameter]
            byteStr = byteStr[parameter:]
            freqList[int(word, 2)] += 1

    # example:
    #   parameter = 2
    #   freqList[5] = 5      '0101' letter is found 5 times
    #   array index is the letter in decumal and the value is its frequency

    # The remaining bits of the file that don't fit
    # in the parameter length will be stored as a tail
    tail = ''
    if len(byteStr) > 0:
        tail = byteStr

    debug('Tail: ', tail, '\n')

    # create a list of (frequency, byteValue, encodingBitStr) tuples
    tupleList = []
    for b in range(2**parameter):
        if freqList[b] > 0:
            tupleList.append((freqList[b], b, ''))

    # sort the list according to the frequencies descending
    tupleList = sorted(tupleList, key=lambda tup: tup[0], reverse = True)

    debug('tupleList: ', tupleList, '\n')

    print('--- bitifying {} seconds ---\n'.format(time.time() - mid_time))
    mid_time = time.time()

    shannon_fano_encoder(0, len(tupleList) - 1)

    debug('bitified tupleList: ', tupleList, '\n')

    print('--- encoding {} seconds ---'.format(time.time() - mid_time))
    mid_time = time.time()

    debug('\nThe list of (frequency, byteValue, encodingBitStr) tuples:\n',
          tupleList, '\n')

    dic = dict([(tup[1], tup[2]) for tup in tupleList])
    del tupleList # unneeded anymore

    debug('The dictionary of byteValue : encodingBitStr pairs:\n', dic, '\n')

    # write a list of (byteValue,3-bit(len(encodingBitStr)-1),encodingBitStr)
    # tuples as the compressed file header
    bitStream = ''
    fo = open(outputFile, 'wb')

    parameterBitStr = bin(parameter) # first we write the parameter
    parameterBitStr = parameterBitStr[2:] # remove 0b
    # add 0's if needed for 5 bits
    parameterBitStr = '0' * (5 - len(parameterBitStr)) + parameterBitStr
    byteWriter(parameterBitStr, fo)
    debug('parameterBitStr:', parameterBitStr)

    tailLengthBitStr = bin(len(tail)) # then we write the length of the tail
    tailLengthBitStr = tailLengthBitStr[2:]
    tailLengthBitStr = '0' * (5 - len(tailLengthBitStr)) + tailLengthBitStr
    byteWriter(tailLengthBitStr, fo)

    debug('tailLengthBitStr:', tailLengthBitStr)

    # TODO make it '5'
    debug("tail: ", end='')
    if len(tail) > 0:
        byteWriter(tail, fo)
        debug(tail,end='')
    else:
        debug("NONE",end='')
    debug()

    # then we write the number of encoding tuples
    dicLengthBitStr = bin(len(dic) - 1)
    dicLengthBitStr = dicLengthBitStr[2:]
    dicLengthBitStr = \
        '0' * (parameter - len(dicLengthBitStr)) + dicLengthBitStr
    debug('bitStream bf dic len: ', bitStream)

    byteWriter(dicLengthBitStr, fo)
    debug('bitStream af dic len: ', bitStream)
    debug('\ndicLengthBitStr:', dicLengthBitStr)

    debug('dic length:', len(dic), '\n')

    for (byteValue, encodingBitStr) in dic.items():
        bitStr = bin(byteValue)
        bitStr = bitStr[2:]
        bitStr = '0' * (parameter - len(bitStr)) + bitStr
        byteWriter(bitStr, fo)

        encodedLenBitStr = bin(len(encodingBitStr))
        encodedLenBitStr = encodedLenBitStr[2:]
        encodedLenBitStr = \
            '0' * (parameter - len(encodedLenBitStr)) + encodedLenBitStr

        debug('pre-bitstr', bitStream)
        byteWriter(encodedLenBitStr, fo)
        debug('enc', encodedLenBitStr)

        debug('bitStream in for loop bf: ', bitStream)
        byteWriter(encodingBitStr, fo)
        debug('bitStream in for loop af: ', bitStream)
        debug('post-bitstr', bitStream)
        debug('encoded dict element: ',
              bitStr, encodedLenBitStr, encodingBitStr,sep='', end='\n\n')

    byteStr = ''
    debug('encoded letters: ', end='')
    for byte in byteArr:
        bitStrem = BitStream()
        bitStrem.write(byte, int8)
        byteStr += str(bitStrem)
        while len(byteStr) >= parameter:
            word = byteStr[:parameter]
            byteStr = byteStr[parameter:]
            byteWriter(dic[int(word, 2)], fo)
            debug(dic[int(word,2)], end='')
    debug()

    debug('bitStream before nullTail: ', bitStream)

    nullTail =  8 - len(bitStream)

    byteWriter('0' * 8, fo) # to write the last remaining bits (if any)
    debug('Write last remaining bits (if any):')
    debug('    bitStr before calling byteWriter:', '0'*8, end='')
    debug()
    debug('    bitStream before calling byteWriter:', bitStream)

    fo.write(bytes([nullTail]))
    debug('the last byte (with tail): {:08b}'.format(nullTail))
    debug('nullTailLength:', nullTail, '\n')
    fo.close()
    print('--- code table {} seconds ---\n'.format(time.time() - mid_time))
    mid_time = time.time()
    fileSize = os.path.getsize(outputFile) # fileSize = len(byteArr)
    if fileSize < 1000:
        print('Compressed file size {} B\n'.format(fileSize))
    elif fileSize < 10**6:
        print('Compressed file size {} KB\n'.format(fileSize/10**3))
    else:
        print('Compressed file size {} MB\n'.format(fileSize/10**6))

# =============================================================================
# Decoding
# =============================================================================

# example:
#   mode = 'd'
#   inputFile = './encoded.bin'
#   outputFile = './decoded.txt'

if mode == 'd':
    bitPosition = 0
    parameter = int(bitReader(5), 2) # First read the parameter
    debug('parameter =', parameter)
    tailLength = int(bitReader(5), 2)
    debug('tailLength =', tailLength, '\n')
    if tailLength > 0:
        tail = int(bitReader(tailLength), 2)
        tail = bin(tail)
        tail = tail[2:]
        tail = '0' * (tailLength - len(tail)) + tail
        debug(tail)
    # then read the number of encoding tuples
    n = int(bitReader(parameter), 2) + 1
    debug('Number of encoding tuples:', n)
    dic = dict()
    debug('par:', parameter, 'tailLen:', tailLength, 'dicLen:', n, '\n')
    if n > 0:
        for i in range(n):
            # read the byteValue
            byteValue = bitReader(parameter)

            m = int(bitReader(parameter), 2) # m = kodo ilgis
            # -------
            # m = 3
            # -------
            # read encodingBitStr
            debug('m =', m)
            encodingBitStr = bitReader(m)
            dic[encodingBitStr] = byteValue # add to the dictionary
            debug('w:', byteValue, 'l:', m, 'c:', encodingBitStr)
            debug('The dictionary of encodingBitStr : byteValue pairs:')
            debug(dic, '\n')

    # read the encoded data, decode it, write into the output file
    fo = open(outputFile, 'wb')
    bitStream = ''
    encodingBitStr = ''
    while True:
        # read bits until a decoding match is found
        bit = bitReader(1)
        if bit == '':
            break
        encodingBitStr += bit
        if encodingBitStr in dic:
            debug('encBitStr: ', encodingBitStr)
            byteValue = dic[encodingBitStr]
            byteWriter(byteValue, fo)
            encodingBitStr = ''

    lastByte = bin(byteArr[len(byteArr) - 2])
    lastByte = lastByte[2:]
    lastByte = '0' * (8 - len(lastByte)) + lastByte

    for i in range(byteArr[len(byteArr) - 1]):
        lastByte = lastByte[:-1]

    debug('lastByte: ', lastByte)

    for bit in lastByte:
        debug('bit: ', bit)
        encodingBitStr += bit
        if encodingBitStr in dic:
            debug('encBitStr: ', encodingBitStr)
            byteValue = dic[encodingBitStr]
            byteWriter(byteValue, fo)
            encodingBitStr = ''

    if tailLength > 0:
        debug('tailLength > 0')
        byteWriter(tail, fo)

    debug('bitStream bf last:write ', bitStream)

    byteWriter('0' * 8, fo)
    fo.close()

print('--- {} seconds ---'.format(time.time() - start_time))
