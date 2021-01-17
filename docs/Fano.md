
## example no.1
```
# original file:
'12 01' (in Hex) -> 0001 0010  0000 0001
frequencies:
    00 * 5, code =  '0'
    01 * 2, code = '10'
    10 * 1, code = '11'

# encoded with tables

00010 [0000]     [10]            |"00"[01]'0'            "01"[10]'10'   "10"[10]'11'   |0.10.0.11.0.0.0.10    0                00000001
k=2   tail.len=0 dict.len=2+1=3  |"letter"[length]'code'                               |encoded text          |trailing zeroes |last byte holding nullTail (=1)
                                                                            | 
                                                                            | beginning of a 4th byte here
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

# encoded with tables

00010 000    | 0   10                00      01         0    |  01   10  10     11  |  10   11  0110 | 10 000000             | 00000110

k=2   tail_len=0   dict_len=2+1=3   "00"    [01]       '0'   | "01" [10] '10'  "11" | [10] '11' 0110 | 10 | six trailing     | last byte to hold nullTail len (=6 =110)
                   |                letter  code_len   code     l    cl   c     l      cl   c   |         | zeroes (nullTail | and its zero padding (5 leading zeroes)
      no following |                                                                            |         | len = 6)         |
      bits to hold |                                                                            |         
      the tail     | from here starts the information about the tables                          | "body" (encoded letters) starts from here
      itself       |                                                                            |
                   |                                                                            | it should be:
                                                                                                | 011010
# encoded with binary tree

00010 000    | 0   

k=2   tail_len=0   
                   |                 
      no following |                    
      bits to hold |                    
      the tail     | tree starts from here
      itself       |                      
                   |                      
```
