# Extract Email

I have a lot of alerts for various research articles I am interested in with [Google Scholar](https://scholar.google.com/). This generates a lot of email each week that needs to be sifted. I developed this simple tool to help me. It can read emails from Google Scholar and www.researchgate.net for links to articles. You have to save the emails to `.eml` format somewhere on your disk. Point the script to that folder and it will read and find all `href` tags. It will deduplicate the links and list the links along with the description. Optionally, it can load PDF links directly in your browser or open a CSV list of links up in your favorite spreadsheet.

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

