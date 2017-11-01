# About this repo

This repo contains various tools used for the [Connected Open Heritage project](Connected Open Heritage).

## Process various wikipages

The scripts in the root catalogue are for creating mapping tables and such:

* **create_distinct_lookup_table.py** – create a table [like this](https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/se-arbetsl_(sv)/types) from distinct values in a column
* **create_mapping_tables.py** – create a table [like this](https://www.wikidata.org/w/index.php?title=Wikidata:WikiProject_WLM/Mapping_tables/es-vc_(ca)&oldid=418466520) using _template.txt
* **create_progress.py** – create an empty [progress table](https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/Status)
* **lookup_table_to_json.py** – download a lookup table and convert it to a JSON file [like this](https://gist.github.com/Vesihiisi/5ae8d5715d93cd77543edbb2e6d5d855)
* **wlmhelpers.py** – utilities for interacting with MySQL database

## Dataset scripts

Each of the tables in the WLM database has a separate script that extracts the data, processes it and uploads it to Wikidata. The script is named after the namespace + language combination of the table, eg. `monuments_at_(de)` -> `AtDe.py`.

Run the specific script to import the data, using your MySQL credentials and optional flags:

```
python3 AtDe.py --host localhost --user foo --password bar --db wlm --short --upload live
```

If you're running the script on the Toollabs server, leave out `host`, `db`, `user` and `passwords`, as these will be filled out automatically. 

This will process the `monuments_at_(de)` table.

`short` will only process the first 10 rows in the table, optionally you can add a digit to choose how many rows will be processed, eg. `short 15`.

`upload` to upload the created claims to Wikidata. You can leave it out if you want to debug the Monument object processing. **By default** this will use the [Wikidata Sandbox](https://www.wikidata.org/wiki/Q4115189). Add `live` to work on actual live Wikidata items, assuming you're 100% positive you want to do that.

`table` will generate a preview file of how the data would be processed, ready to paste into a Wiki page, eg. https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/at_(de)/preview.

**Monument.py** – A general Monument class with methods that are shared by all the dataset-specific classes.

**Uploader.py** – converts Monument objects into Wikidata-ready data dictionaries and uploads them. Currently locked to the Wikidata sandbox.

**Logger.py** – logs each Wikidata write.

**importer_utils.py** – various data processing functions used by Monument.py