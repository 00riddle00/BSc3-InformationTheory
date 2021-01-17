```
# orig failas:
'1' (ascii = 31h = 0011 0001)
dazniai:
    00 * 2, kodas =  '0'
    01 * 1, kodas = '10'
    11 * 1, kodas = '11'

# encoded su lentelemis

00010 000    | 0 10              00   01          0     |  01  10  10    11     | 10  11  0110 | 10 000000 | 00000110

k=2   tail_len=0 dict_len=2+1=3 "00"  01         '0'    | "01" 10 '10'  "11"    | 10 '11' 0110   10
                 |              zodis ilgis_kodo kodas     z   i   k     z        i   k   |
                 |                                                                        |
                 |                                                                        |
                 | nuo cia prasideda lenteliu informacija                                 | nuo cia prasideda "body"
                 |                                                                        |
                 |                                                                        |
                 |                                                                        | body turi buti toks:
                                                                                          | 011010

# encoded su medziu

00010 000    | 0 

00010 000      0 
k=2   tail_len=0 
                 
                 |
                 | nuo cia medis prasideda
                 |
```
