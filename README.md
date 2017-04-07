# About this repo

This repo contains various tools used for the [Connected Open Heritage project](Connected Open Heritage).

## Process various wikipages

The scripts in the root catalogue are for creating mapping tables and such:

* **create_distinct_lookup_table.py** – create a table [like this](https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/se-arbetsl_(sv)/types) from distinct values in a column
* **create_mapping_tables.py** – create a table [like this](https://www.wikidata.org/w/index.php?title=Wikidata:WikiProject_WLM/Mapping_tables/es-vc_(ca)&oldid=418466520) using _template.txt
* **create_progress.py** – create an empty [progress table](https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/Status)
* **lookup_table_to_json.py** – download a lookup table and convert it to a JSON file [like this](https://gist.github.com/Vesihiisi/5ae8d5715d93cd77543edbb2e6d5d855)
* **wlmhelpers.py** – utilities for interacting with MySQL database

## Importer

This the part that actually extracts the data from the WLM database, processes it and uploads it to Wikidata:

**importer.py** – the main script. Pass your MySQL credentials to it:

```
python3 importer.py --host localhost --user foo --password bar --db wlm --country se-fornmin --language sv --short --upload live
```

If you're running the script on the Toollabs server, leave out `host`, `db`, `user` and `passwords`, as these will be filled out automatically. 

This will process the `monuments_se-fornmin_(sv)` table.

`short` will only process the first 10 rows in the table.

`upload` to upload the created claims to Wikidata. You can leave it out if you want to debug the Monument object processing. **By default** this will use the [Wikidata Sandbox](https://www.wikidata.org/wiki/Q4115189). Add `live` to work on actual live Wikidata items, assuming you're 100% positive you want to do that.

Each row in the database is used to create a Monument object using data from the SPECIFIC_TABLES dictionary, which maps database tables to classes and, optionally, extra data files that can be passed to the constructor.

**Monument.py** – Monument classes. Includes both a general parent class Monument() and special child classes that inherit from it, one per database table. Those are used to process table-specific data.

**Uploader.py** – converts Monument objects into Wikidata-ready data dictionaries and uploads them. Currently locked to the Wikidata sandbox.

**Logger.py** – logs each Wikidata write.

**importer_utils.py** – various data processing functions used by Monument.py