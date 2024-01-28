# tagbiljett

A command-line tool for querying SJ ticket prices

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install tagbiljett.

```bash
pip install tagbiljett
```

## Usage

```
> tagbiljett --help

Usage: tagbiljett [OPTIONS] %Y-%m-%dT%H:%M FROM TO

  Query current SJ ticket prices for a given journey

Options:
  -a, --arrival %Y-%m-%dT%H:%M  Arrival date and time.
  -n, --changes INTEGER         Exact number of changes.
  -h, --help                    Show this message and exit.
```

```
> ./cron.sh trains.csv prices.txt
```

Using the container:
```
> docker run ghcr.io/jwindhager/tagbiljett --help

Usage: tagbiljett [OPTIONS] %Y-%m-%dT%H:%M FROM TO

  Query current SJ ticket prices for a given journey

Options:
  -a, --arrival %Y-%m-%dT%H:%M  Arrival date and time.
  -n, --changes INTEGER         Exact number of changes.
  -h, --help                    Show this message and exit.
```

```
> docker run -v trains.csv:/usr/src/app/trains.csv -v tagbiljett-data:/usr/src/app/data --entrypoint /bin/bash ghcr.io/jwindhager/tagbiljett cron.sh trains.csv data/prices.txt
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://github.com/jwindhager/tagbiljett/blob/main/LICENSE)
