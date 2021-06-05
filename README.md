# Extract Email

A simple tool that can read emails from Google Scholar and www.researchgate.net for links to articles. It will deduplicate the links. Optionally, it can load PDF links directly in your browser or open a CSV list of links up in your favorite spreadsheet.

Clone the repository and:

```bash
$ make
```

Activate the virtual environment:
```bash
$ . .venv/bin/activate
```

Execute the script:
```bash
$ extract "~/tmp/extract tbird email" --verbose --launch-pdf
```

OR

```bash
$ extract "~/tmp/extract tbird email" --verbose --launch-csv
```

## License

[MIT](https://choosealicense.com/licenses/mit/)

