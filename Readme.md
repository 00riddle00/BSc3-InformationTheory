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
cd tests/

TESTFILE="black.bmp" # select from assets/
PARAMETER=2          # select k in 2..32

./test_fano.py  e assets/"$TESTFILE"                   results/fano/encoded."$TESTFILE".bin $PARAMETER
./test_fano.py  d results/fano/encoded."$TESTFILE".bin results/fano/decoded."$TESTFILE"
diff -s           assets/"$TESTFILE"                   results/fano/decoded."$TESTFILE"

# Any newly created encoded (.bin) and decoded (.png, .bmp, .txt, ...) files
# in Results/ folder during tests are ignored by git (see .gitignore)
```
