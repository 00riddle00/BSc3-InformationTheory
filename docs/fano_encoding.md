
## example no.1
```
# original file:
'12 01' (in Hex) -> 0001 0010  0000 0001
frequencies:
    00 * 5, code =  '0'
    01 * 2, code = '10'
    10 * 1, code = '11'

# ===================
# encoded with tables
# ===================

00010000 01000010 01101010 10110100 11000100 00000001

00010  000|0       10                00  01  0             |  01  10  10     10  |  10  11    0 10 0 | 11 0 0 0 10    0                  00000001
00010 [000|0]     [10]              "00"[01]'0'            | "01"[10]'10'   "10" | [10]'11'   0.10.0 | 11.0.0.0.10    0                | 00000001
k=2   tail.len=0  dict.len=2+1=3  | "letter"[length]'code'                                    | encoded text        | trailing zeroes  | last byte holding nullTail (=1)
                                  |                                                           |                     |                  |
                                                                             
"00" = letter                                                               
[01] = its code's length                                                    
'0'  = its code
```

## example no.2
```
# original file:
'1' (in ASCII) -> 31h -> 0011 0001
frequencies:
    00 * 2, code =  '0'
    01 * 1, code = '10'
    11 * 1, code = '11'

# ===================
# encoded with tables
# ===================

00010000 01000010 01101011 10110110 10000000 00000110

00010 000    | 0    10                00      01         0    |  01   10  10     11  |  10   11  0110 | 10           000000           | 00000110
00010 000    | 0    10               "00"    [01]       '0'   | "01" [10] '10'  "11" | [10] '11' 0110 | 10           000000           | 00000110
k=2   tail_len=0   |dict_len=2+1=3   letter  code_len   code     l    cl   c     l      cl   c   |                 | six trailing     | last byte to hold nullTail len (=6 =110)
      no following |                                                                             |                 | zeroes (nullTail | ant its zero padding (5 leading zeroes)
      bits to hold |                                                                             |                 | len = 6)
      the tail     | here starts the information about the tables                                | "body" (encoded 
      itself       |                                                                             | letters) starts 
                   |                                                                             | here
                   |                                                                             |
                   |                                                                             | it should be:
                                                                                                 | 0.11.0.10
# ========================
# encoded with binary tree
# ========================

00010000 01000101 11101101 00000000 00000111

00010 000    | 0     1               00                0                1               01 |              1                11                 01101 | 0    0000000           | 00000111
00010 000    | 0     1              "00"               0                1              "01"|              1               "11"                01101 | 0    0000000           | 00000111
k=2   tail_len=0   | v1.left.child | v1.left.child's | v1.right.child | v2.left.child | v2.left.child's | v2.right.child | v2.right.child's |             | seven trailing   | last byte to hold nullTail len (=6 =110)
                   | is a leaf     | value           | is not a leaf  | is a leaf     | value           | is a leaf      | value            |             | zeroes (nullTail | ant its zero padding (5 leading zeroes)
                   |                                                  |                |                                 |                  |             | len = 7)
                   |                                                  | (end of v1)    |                                 | (end of v2)      |             |            
      no following | tree starts here                                                                                                       | body starts
      bits to hold |                                                                                                                        | here
      the tail     |         v1                                                                                                             | 
      itself       |       0/  \1  <- these '0's and '1's on branches                                                                       | it should be:
                   |       /    \          are only used for decoding                                                                       | 0.11.0.10
                   |     "00"    v2             
                   |           0/  \1             
                   |           /    \            
                   |         "01"   "11"
```
