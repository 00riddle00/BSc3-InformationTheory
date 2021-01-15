#!/usr/bin/env python3
import sys
import os
from bitstream import BitStream
from numpy import *
import time

# Shannon-Fano Coding for Lossless Data Compression

def shannon_fano_encoder(iA, iB): # iA to iB : index interval
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

def byteWriter(bitStr, outputFile):
  global bitStream
  bitStream += bitStr
  while len(bitStream) > 8: # write byte(s) if there are more then 8 bits
    byteStr = bitStream[:8]
    bitStream = bitStream[8:]
    outputFile.write(bytes([int(byteStr, 2)]))

def bitReader(n): # number of bits to read
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

if len(sys.argv) < 4:
  print('Usage: ShannonFano.py [e|d] [path]InputFileName [path]OutputFileName parameter')
  exit()
mode = sys.argv[1] # encoding/decoding

inputFile = sys.argv[2]
outputFile = sys.argv[3]

# mode = 'e'
# inputFile = "./input.txt"
# outputFile = "./encoded.bin"

# mode = 'd'
# inputFile = "./encoded.bin"
# outputFile = "./decoded.txt"

if os.stat(inputFile).st_size == 0:
  sys.exit("The provided file is empty!")

fileSize = os.path.getsize(inputFile)
fi = open(inputFile, 'rb')
byteArr = bytearray(fi.read(fileSize))

fi.close()
fileSize = len(byteArr)
if fileSize < 1000:
  print('Input file size {} B'.format(fileSize))
elif fileSize < 10**6:
  print('Input file size {} KB'.format(fileSize/10**3))
else:
  print('Input file size {} MB'.format(fileSize/10**6))
print()

start_time = time.time()

if mode == 'e': # FILE ENCODING

  parameter = int(sys.argv[4])
  # parameter = 2
  # freqList[5] = 5      0101 is found 5 times
  # array index is the bit that is needed and the value is it's frequency

  freqList = [0] * 2**parameter #galima kažkaip optimizint
  byteStr = ""
  for byte in byteArr:
    bitStrem = BitStream()
    bitStrem.write(byte, int8)
    byteStr += str(bitStrem)
    while len(byteStr) >= parameter:
      word = byteStr[:parameter]
      byteStr = byteStr[parameter:]
      freqList[int(word, 2)] += 1

  # The leftovers from the file that don't fit in the parameter will be stored as a tail
  tail = ''
  if len(byteStr) > 0:
    tail = byteStr

  # print("Tail: ", tail)

  # create a list of (frequency, byteValue, encodingBitStr) tuples
  tupleList = []
  for b in range(2**parameter):
    if freqList[b] > 0:
      tupleList.append((freqList[b], b, ''))

  # sort the list according to the frequencies descending
  tupleList = sorted(tupleList, key=lambda tup: tup[0], reverse = True)

  shannon_fano_encoder(0, len(tupleList) - 1)
  # print('The list of (frequency, byteValue, encodingBitStr) tuples:')
  # print(tupleList)
  # print()

  dic = dict([(tup[1], tup[2]) for tup in tupleList])
  del tupleList # unneeded anymore
  # print 'The dictionary of byteValue : encodingBitStr pairs:'
  # print(dic)

  # write a list of (byteValue,3-bit(len(encodingBitStr)-1),encodingBitStr)
  # tuples as the compressed file header
  bitStream = ''
  fo = open(outputFile, 'wb')

  parameterBitStr = bin(parameter) # first we write the parameter
  parameterBitStr = parameterBitStr[2:] # remove 0b
  parameterBitStr = '0' * (5 - len(parameterBitStr)) + parameterBitStr # add 0's if needed for 5 bits
  byteWriter(parameterBitStr, fo)
  # print(parameterBitStr,end='')

  tailLengthBitStr = bin(len(tail)) # then we write the length of the tail
  tailLengthBitStr = tailLengthBitStr[2:]
  tailLengthBitStr = '0' * (4 - len(tailLengthBitStr)) + tailLengthBitStr
  byteWriter(tailLengthBitStr, fo)
  # print(tailLengthBitStr,end='')

  if len(tail) > 0:
    byteWriter(tail, fo)
    # print(tail,end='')

  dicLengthBitStr = bin(len(dic) - 1) # then we write the number of encoding tuples GALIMAI PROBLEMA
  dicLengthBitStr = dicLengthBitStr[2:]
  dicLengthBitStr = '0' * (parameter - len(dicLengthBitStr)) + dicLengthBitStr
  byteWriter(dicLengthBitStr, fo)
  # print(dicLengthBitStr,end='')

  # print "dic length", len(dic)

  for (byteValue, encodingBitStr) in dic.items():
    bitStr = bin(byteValue)
    bitStr = bitStr[2:]
    bitStr = '0' * (parameter - len(bitStr)) + bitStr
    byteWriter(bitStr, fo)

    encodedLenBitStr = bin(len(encodingBitStr))
    encodedLenBitStr = encodedLenBitStr[2:]
    encodedLenBitStr = '0' * (parameter - len(encodedLenBitStr)) + encodedLenBitStr

    # print('pre-bitstr', bitStream)
    byteWriter(encodedLenBitStr, fo)
    # print('enc', encodedLenBitStr)

    byteWriter(encodingBitStr, fo)
    # print('post-bitstr', bitStream)
    # print(bitStr, encodedLenBitStr, encodingBitStr,end='',sep='')

  byteStr = ""
  for byte in byteArr:
    bitStrem = BitStream()
    bitStrem.write(byte, int8)
    byteStr += str(bitStrem)
    while len(byteStr) >= parameter:
      word = byteStr[:parameter]
      byteStr = byteStr[parameter:]
      byteWriter(dic[int(word, 2)], fo)
      # print(dic[int(word,2)], end='')
  # print()
  nullTail =  8 - len(bitStream)
  byteWriter('0' * 8, fo)
  # print('0'*8,end='') # to write the last remaining bits (if any)
  # print('\n',bitStream)
  # fo.write(chr(nullTail))

  fo.write(bytes([nullTail]))
  # print('0'*8, str(bin(nullTail))[2:],sep='')
  # print()
  # print("nullTailLength", nullTail)
  fo.close()

  fileSize = os.path.getsize(outputFile)
  # fileSize = len(byteArr)
  if fileSize < 1000:
    print('Compressed file size {} B'.format(fileSize))
  elif fileSize < 10**6:
    print('Compressed file size {} KB'.format(fileSize/10**3))
  else:
    print('Compressed file size {} MB'.format(fileSize/10**6))
  print()


#############################################

elif mode == 'd': # FILE DECODING
  bitPosition = 0
  parameter = int(bitReader(5), 2) # First read the parameter
  # print parameter
  tailLength = int(bitReader(4), 2)
  # print tailLength
  if tailLength > 0:
    tail = int(bitReader(tailLength), 2)
    tail = bin(tail)
    tail = tail[2:]
    tail = '0' * (tailLength - len(tail)) + tail
    # print tail
  n = int(bitReader(parameter), 2) + 1 # then read the number of encoding tuples
  # print 'Number of encoding tuples:', n
  dic = dict()
  # print('par:', parameter, 'tailLen:', tailLength, 'dicLen:',n)
  if n > 0:
    for i in range(n):
      # read the byteValue
      byteValue = int(bitReader(parameter), 2)
      byteValue = bin(byteValue)
      byteValue = byteValue[2:]
      byteValue = '0' * (parameter - len(byteValue)) + byteValue


      m = int(bitReader(parameter), 2) # m = kodo ilgis
      # -------
      # m = 3
      # -------
      # read encodingBitStr
      #print("m=", m)
      encodingBitStr = bitReader(m)
      dic[encodingBitStr] = byteValue # add to the dictionary
      # print('w:', byteValue, 'l:', m, 'c:', encodingBitStr)
    # print 'The dictionary of encodingBitStr : byteValue pairs:'
    # print(dic)
    # print

  # read the encoded data, decode it, write into the output file
  fo = open(outputFile, 'wb')
  bitStream = ''
  encodingBitStr = ''
  while True:
    # read bits until a decoding match is found
    bit = bitReader(1)
    if bit == "":
      break
    encodingBitStr += bit
    if encodingBitStr in dic:
      byteValue = dic[encodingBitStr]
      byteWriter(byteValue, fo)
      encodingBitStr = ''

  lastByte = bin(byteArr[len(byteArr) - 2])
  lastByte = lastByte[2:]
  lastByte = '0' * (8 - len(lastByte)) + lastByte

  for i in range(byteArr[len(byteArr) - 1]):
    lastByte = lastByte[:-1]

  for bit in lastByte:
    encodingBitStr += bit
    if encodingBitStr in dic:
      byteValue = dic[encodingBitStr]
      byteWriter(byteValue, fo)
      encodingBitStr = ''

  if tailLength > 0:
    byteWriter(tail, fo)

  byteWriter('0' * 8, fo)
  fo.close()

print("--- {} seconds ---".format(time.time() - start_time))
