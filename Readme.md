## Information Theory

- A2. Fano coding
- B2. Adaptive Huffman coding

### Setup environment (linux)
```
python3 -m venv env
source env/bin/activate
./env/bin/python3 -m pip install --upgrade pip
./env/bin/python3 -m pip install -r requirements.txt
```

### Run tests
```
cd Tests/

TESTFILE="black.bmp" # select from Assets/
PARAMETER=2          # k = 2..24

./testerFano.py e Assets/"$TESTFILE"                   Results/Fano/encoded."$TESTFILE".bin $PARAMETER
./testerFano.py d Results/Fano/encoded."$TESTFILE".bin Results/Fano/decoded."$TESTFILE"
diff -s           Assets/"$TESTFILE"                   Results/Fano/decoded."$TESTFILE"
```

