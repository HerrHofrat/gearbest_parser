# gearbest_parser

### Status
Work in progress

### Installation
```
python3 setup.py install
```

### Examples
```
>>> from gearbest_parser import GearbestParser
>>>
>>> parser = GearbestParser()
>>> item = parser.load(<url>, <other currency>) # loads a url from gearbest and returns an item class for that. if a currency is defined, the USD price is converted (with the gearbest conversion)
>>> item.name
>>> item.description
>>> item.image
>>> item.price
>>> item.currency
```

### TODO/Contribute
Contributions and Pull Requests always welcome.
