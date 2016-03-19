# crawling-github
let's get it started! 

## Dependencies
- [tinydb](http://tinydb.readthedocs.org/) [3.1.3](https://pypi.python.org/pypi/tinydb/3.1.3)
```
pip install tinydb
```
- [requests](http://docs.python-requests.org/)
```
pip install requests
```

## Run
`cd` to repository directory and
```
python3 src/main.py [<req gap>]
```
`<req gap>` gives gap in seconds held for every request. E.g. `0.2`, `random.uniform(1, 3)`(default).

## Results
Results will be in `./data/db.tinydb`.

**DON'T PUSH DATA!**
