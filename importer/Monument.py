from os import path
import json
import importer_utils as utils

MAPPING_DIR = "mappings"
P31_BLACKLIST = utils.load_json(path.join(MAPPING_DIR, "P31_blacklist.json"))


class Monument(object):

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        """
        Initialize the data object.

        :param db_row_dict: raw data from the database
        :param mapping: mapping file object
        :param data_files: resources like dictionaries of known placenames to match
        :param existing: list of Wikidata items using a specific property
            that is optionally specified in the mapping file and is supposed to
            hold unique values
        :param repository: data repository (Wikidata site)
        """
        self.raw_data = db_row_dict
        self.props = data_files["_static"]["props"]
        self.adm0 = data_files["_static"]["adm0"]
        self.sources = data_files["_static"]["sources"]
        self.common_items = data_files["_static"]["common_items"]
        for k, v in db_row_dict.items():
            if not k.startswith("m_spec."):
                setattr(self, k.replace("-", "_"), v)
        self.monuments_all_id = ""
        self.construct_wd_item(mapping)
        self.data_files = data_files
        self.existing = existing
        self.repo = repository
        self.problem_report = {}

    def print_wd(self):
        """Print the data object dictionary on screen."""
        print(
            json.dumps(self.wd_item,
                       sort_keys=True,
                       indent=4,
                       ensure_ascii=False,
                       default=utils.datetime_convert)
        )

    def get_matched_item_p31s(self):
        """Return the p31 value(s) for any matched item."""
        if not self.wd_item["wd-item"]:
            return None
        qid = self.wd_item["wd-item"]
        p31s = utils.get_P31(qid, self.repo)
        if not p31s:
            p31s = ['no value', ]
        return (p31s, self.wlm_url, self.monuments_all_id)

    def print_wd_to_table(self):
        """Generate a wikitext preview table of the data item."""
        table = ""
        labels = self.wd_item["labels"]
        descriptions = self.wd_item["descriptions"]
        aliases = self.wd_item["aliases"]
        disambiguators = self.wd_item["disambiguators"]
        table = table + "'''Labels'''\n\n"
        for k, v in labels.items():
            table += "* '''{key}''': {val}\n\n".format(key=k, val=v)
        table = table + "'''Descriptions'''\n\n"
        for k, v in descriptions.items():
            table += "* '''{key}''': {val}\n\n".format(key=k, val=v)
        table = table + "'''Aliases'''\n\n"
        for k, v in aliases.items():
            for single_alias in v:
                table += "* '''{key}''': {val}\n\n".format(
                    key=k, val=single_alias)
        table += "'''Disambiguators'''\n\n"
        for k, v in disambiguators.items():
            table += "* '''{key}''': {val}\n\n".format(key=k, val=v)
        if self.wd_item["wd-item"] is not None:
            table = table + "'''Possible item''': " + \
                utils.wd_template("Q", self.wd_item["wd-item"]) + "\n\n"
        else:
            table = table + "'''Possible item''': \n\n"
        table_head = "{| class='wikitable'\n|-\n! Property\n! Value\n! Qualifiers\n! References\n"
        table = table + table_head
        statements = self.wd_item["statements"]
        for statement in statements:
            claims = statements[statement]
            for claim in claims:
                value = claim["value"]
                if value is None:
                    continue
                value_to_print = ""
                if utils.string_is_q_item(value):
                    value = utils.wd_template("Q", value)
                    value_to_print += str(value)
                elif "quantity_value" in value:
                    quantity = str(value["quantity_value"])
                    if "unit" in value:
                        value_to_print += "{quantity} {unit}".format(
                            quantity=quantity,
                            unit=utils.wd_template("Q", value["unit"]))
                    else:
                        value_to_print += quantity
                elif "time_value" in value:
                    value_to_print += utils.dict_to_iso_date(
                        value["time_value"])
                elif "monolingual_value" in value:
                    value_to_print += "({lang}) {text}".format(
                        text=value["monolingual_value"],
                        lang=value["lang"])
                else:
                    value_to_print += str(value).strip()
                quals = claim["quals"]
                refs = claim["refs"]
                quals_to_print = ""
                if len(quals) == 0:
                    quals_to_print = quals_to_print
                else:
                    for q in quals:
                        quals_to_print = quals_to_print + "<br>" + utils.wd_template(
                            "P", q) + " : " + json.dumps(quals[q])
                if len(refs) == 0:
                    ref_to_print = ""
                else:
                    for r in refs:
                        ref_to_print = json.dumps(
                            r, default=utils.datetime_convert)
                table = table + "|-\n"
                table = table + "| " + utils.wd_template("P", statement) + "\n"
                table = table + "| " + value_to_print + "\n"
                table = table + "| " + quals_to_print + "\n"
                table = table + "| " + ref_to_print + "\n"
        table = table + "|}\n"
        table = table + "----------\n"
        return table

    def add_statement(self, prop_name, value, quals=None, refs=None,
                      if_empty=False):
        """
        Add a statement to the data object.

        If the given property already exists, this will
        append another value to the array,
        i.e. two statements with the same prop.

        Refs is None as default. This means that
        if it's left out, the WLM reference will be inserted
        into the statement. The same if its value is
        set to True. In order to use a custom reference
        or more than one reference, it is inserted here as
        either a single reference or a list of references,
        respectively.
        In order to not use any reference whatsoever,
        the value of refs is to be set to False.

        :param prop_name: name of the property,
            as stated in the props library file
        :param value: the value of the property
        :param quals: a dictionary of qualifiers
        :param refs: a list of references or a single reference.
            Set None/True for the default reference,
            set False to not add a reference.
        :param if_empty: If statement should only be added if this property
            doesn't already have a value. Defaults to False.
        """
        base = self.wd_item["statements"]
        prop = self.props[prop_name]
        qualifiers = {}
        if prop not in base:
            base[prop] = []
        if quals is not None and len(quals) > 0:
            for k in quals:
                prop_name = self.props[k]
                qualifiers[prop_name] = quals[k]
        if refs is None or refs is True:
            refs = self.wlm_source
        elif refs is False:
            refs = []

        if refs and not isinstance(refs, list):
            refs = [refs]
        statement = {"value": value, "quals": qualifiers, "refs": refs,
                     "if_empty": if_empty}
        base[prop].append(statement)

    def remove_statement(self, prop_name):
        """
        Remove all statements with a given property from the data object.

        :param prop_name: name of the property,
            as stated in the props library file
        """
        base = self.wd_item["statements"]
        prop = self.props[prop_name]
        if prop in base:
            del base[prop]

    def substitute_statement(self, prop_name, value, quals=None, refs=None):
        """
        Instead of adding to the array, replace the statement.

        This is so that instances of child classes
        can override default values...
        For example p31 museum -> art museum
        """
        base = self.wd_item["statements"]
        prop = self.props[prop_name]
        if prop not in base:
            base[prop] = []
            self.add_statement(prop_name, value, quals, refs)
        else:
            self.remove_statement(prop_name)
            self.add_statement(prop_name, value, quals, refs)

    def get_statement_values(self, prop_name):
        """
        Retrieve list of all statements with given property from data object.

        e.g. get_statement_values("country") → ['Q29']

        :param prop_name: name of the property,
            as stated in the props library file
        """
        base = self.wd_item["statements"]
        prop = self.props[prop_name]
        if prop in base:
            return [x['value'] for x in base[prop]]

    def set_wd_item(self, wd_item):
        """Associate the data object with a Wikidata item."""
        if wd_item is not None:
            self.wd_item["wd-item"] = wd_item
            print("Associated WD item: ", wd_item)

    def add_label(self, language, text):
        """
        Add a label in a specific language.

        :param language: code of language, e.g. "fi"
        :param text: content of the label
        """
        base = self.wd_item["labels"]
        base[language] = text

    def add_alias(self, language, text):
        """
        Add an alias in a specific language.

        :param language: code of language, e.g. "fi"
        :param text: content of the alias
        """
        base = self.wd_item["aliases"]
        if language not in base:
            base[language] = []
        base[language].append(text)

    def add_description(self, language, text):
        """
        Add a description in a specific language.

        :param language: code of language, e.g. "fi"
        :param text: content of the description
        """
        base = self.wd_item["descriptions"]
        base[language] = text

    def add_disambiguator(self, text, language=None):
        """
        Add a disambiguator, optionally for a specific language.

        The disambiguator is added to the description in case of there being
        identical label/description pairs, otherwise it is not used.

        :param text: content of the disambiguator
        :param language: language, in the event the disambiguator cannot be
            used for all languages.
        """
        language = language or '_default'
        base = self.wd_item["disambiguators"]
        base[language] = text

    def set_country(self):
        """Set the country using the mapping file."""
        code = self.mapping["country_code"].lower()
        country = [item["item"]
                   for item in self.adm0 if item["code"].lower() == code][0]
        self.add_statement("country", country)

    def set_is(self):
        """
        Set the P31 property using the mapping file or global default.

        This only gets used if there isn't already a P31 value.
        """
        default_is = (self.mapping.get("default_is") or
                      self.common_items["cultural_property"])
        self.add_statement("is", default_is["item"], if_empty=True)

    def set_labels(self, language, content):
        """
        Add a label in a specific language using content with markup.

        This will clean up markup, for instance if it's a Wiki-link
        it will extract its title.

        :param language: code of language, e.g. "fi"
        :param text: content of the label
        """
        self.add_label(language, utils.remove_markup(content))

    def set_heritage(self):
        """Set the heritage status, using mapping file."""
        if "heritage" in self.mapping:
            heritage = self.mapping["heritage"]
            self.add_statement("heritage_status", heritage["item"])

    def set_coords(self, coord_keywords_tuple=None):
        """
        Add coordinates.

        :param coord_keywords_tuple: optionally, names of the columns with
            coordinates -- by default ("lat", "lon")
        """
        coord_keywords_tuple = coord_keywords_tuple or ("lat", "lon")
        lat = coord_keywords_tuple[0]
        lon = coord_keywords_tuple[1]
        if (self.has_non_empty_attribute(lat) and
                self.has_non_empty_attribute(lon)):
            if self.lat == 0 and self.lon == 0:
                return
            else:
                latitude = getattr(self, lat)
                longitude = getattr(self, lon)
                self.add_statement(
                    "coordinates", (latitude, longitude))

    def set_monuments_all_id(self, id_keyword):
        """
        Add self.monuments_all_id.

        This is used in order to create url's
        to the monument's post in the API
        (used as sources).

        :param id_keyword: the name of the column to be used
        """
        self.monuments_all_id = str(getattr(self, id_keyword))

    def set_wlm_source(self):
        """
        Create default reference and embed in object.

        Use the monuments_all_id to build url
        to correct post in the API and make reference
        to be used by default with all the statements.
        """
        wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.wlm_source = wlm_source

    def set_image(self, image_keyword="image"):
        """
        Add image.

        :param image_keyword: the name of the column with image path
        """
        if self.has_non_empty_attribute(image_keyword):
            image = getattr(self, image_keyword)
            self.add_statement("image", image, refs=False)

    def set_commonscat(self, keyword="commonscat"):
        """
        Add a statement with Commons category.

        :param keyword: the name of the column with commons category
        """
        if self.has_non_empty_attribute(keyword):
            commonscat = getattr(self, keyword)
            self.add_statement("commonscat", commonscat, refs=False)

    def set_registrant_url(self):
        """Add the registrant url, if present in the data."""
        if self.has_non_empty_attribute("registrant_url"):
            self.wd_item["registrant_url"] = self.registrant_url

    def set_street_address(self, language, address_keyword):
        """
        Add the street address.

        If parsing failed, add to problem report.

        :param language: language code, e.g. "sv"
        :param address_keyword: the name of the column with address
        """
        if self.has_non_empty_attribute(address_keyword):
            possible_address = getattr(self, address_keyword)
            processed_address = utils.get_street_address(
                possible_address, language)
            if processed_address is not None:
                self.add_statement("located_street", processed_address)
            else:
                self.add_to_report(address_keyword, possible_address)

    def get_multi_param_monument_article(self, raw, linked, language,
                                         blocks=None):
        """
        Multi-tiered approach to setting exists_with_monument_article().

        Get the monument_article value in a more complex case where it can
        either be given by a special parameter or be implicitly linked from
        another.

        Common for South American datasets.

        :param raw: the parameter name containing the raw article name
        :param linked: the parameter containing the implicitly linked article
            name (if raw is not provided).
        :param language: language version of wikipedia
        :param blocks: a parameter which blocks both raw and linked. E.g.
            because it allows multiple links to be specified. (optional)
        """
        if blocks and getattr(self, blocks):
            return None
        elif getattr(self, raw):
            return super(self.__class__, self).exists_with_monument_article(
                language, raw)
        else:
            return super(self.__class__, self).exists_with_monument_article(
                language, linked)

    def has_non_empty_attribute(self, attr_name):
        """
        Check whether the data object has a non-empty attribute.

        :param attr_name: name of the attribute
        """
        if hasattr(self, attr_name):
            if getattr(self, attr_name) == "":
                return False
            elif getattr(self, attr_name) is None:
                return False
            else:
                return True
        else:
            return False

    def set_from_dict_match(self, lookup_dict, dict_label, value_label, prop):
        """
        Look up value in dict and add statement on unique match, else report.

        If the value is empty then no statement is added nor is anything
        reported.

        :param lookup_dict: list of dicts to do lookup in
        :param dict_label: value in dict to do matching on
        :param value_label: the label of the value we wish to match
        :prop: the label of the property for which a statement is added
        """
        match_q = None
        if self.has_non_empty_attribute(value_label):
            value = getattr(self, value_label)
            matches = utils.get_item_from_dict_by_key(
                dict_name=lookup_dict,
                search_term=value,
                search_in=dict_label)
            if len(matches) == 1:
                match_q = matches[0]

            if match_q:
                self.add_statement(prop, match_q)
            else:
                self.add_to_report(
                    value_label, value, prop)

    def set_changed(self):
        """Set the 'changed' field."""
        if self.changed:
            self.wd_item["changed"] = self.changed

    def set_source(self):
        """Set the 'source' field if present in source data."""
        if self.has_non_empty_attribute("source"):
            self.wd_item["source"] = self.source

    def create_stated_in_source(self, source_item, pub_date):
        """
        Create a 'stated in' reference.

        :param source_item: Wikidata item or URL used as a source
        :param pub_date: publication date in the format 2014-12-23
        """
        prop_stated = self.props["stated_in"]
        prop_date = self.props["publication_date"]
        pub_date = utils.date_to_dict(pub_date, "%Y-%m-%d")
        return {"source": {"prop": prop_stated, "value": source_item},
                "published": {"prop": prop_date, "value": pub_date}}

    def create_wlm_source(self, monuments_all_id):
        """
        Create a reference to the WLM database.

        :param monuments_all_id: the ID of the object in monuments_all,
            used to create a URL to the entry in the online database.
        """
        self.wlm_url = utils.create_wlm_url(self.mapping["table_name"],
                                            self.mapping["language"],
                                            monuments_all_id)

        source_item = self.sources["monuments_db"]
        timestamp = utils.datetime_object_to_dict(self.wd_item["changed"])
        prop_stated = self.props["stated_in"]
        prop_date = self.props["publication_date"]
        prop_reference_url = self.props["reference_url"]
        return {"source": {"prop": prop_stated, "value": source_item},
                "published": {"prop": prop_date, "value": timestamp},
                "reference_url": {"prop": prop_reference_url,
                                  "value": self.wlm_url}}

    def exists_with_monument_article(self,
                                     language,
                                     article_keyword="monument_article"):
        """
        Get the wd item connected to monument_article (or equivalent), if any.

        Ignore if the linked article contains # in the title,
        indicating a section.
        """
        if self.has_non_empty_attribute(article_keyword):
            article_title = getattr(self, article_keyword)
            if "#" not in article_title:
                wd_item = utils.q_from_wikipedia(language, article_title)
                return wd_item
        else:
            return None

    def exists_with_wd_item(self, wd_item_keyword="wd_item"):
        """Get the Wikidata item connected to wd_item (or equivalent), if any."""
        if wd_item_keyword in self.raw_data:
            return self.raw_data[wd_item_keyword]
        else:
            return None

    def exists_with_prop(self, mapping):
        """
        Get the Wikidata item that has the same value of a property as the data object.

        The unique property is given in the mapping file.
        """
        unique_prop = mapping.get_unique_prop()
        base = self.wd_item["statements"]
        if unique_prop in base:
            val_to_check = base[unique_prop][0]['value']
            if val_to_check in self.existing:
                wd_item = self.existing[val_to_check]
                return wd_item
            else:
                return None

    def in_known_items(self, wd_item):
        """
        Check if given item is in the list of items with a certain property.

        This uses the list of items with a certain property
        (specified in mapping) that was downloaded in the
        beginning of the process.
        """
        return wd_item in self.existing.values()

    def find_matching_wikidata(self, mapping):
        """
        Match the data object with a possible Wikidata item.

        At first, use the downloaded list of Wikidata items
        that use the optional unique property.
        If it contains an item where this property has the same
        value as this data item, assign this Wikidata item
        to this data item.

        If not, do a check using the 'wd_item' and 'monument_article'
        fields. If this results in an item, compare it
        with the downloaded list. If it's found in the list
        then something is wrong, because at this stage it should
        have been found by exists_with_prop()
        and thus we should not have arrived to this stage in the
        first place. So don't upload it (and log it).
        """
        item = self.exists_with_prop(mapping)
        if not item:
            disallowed = [x["item"] for x in P31_BLACKLIST]
            item = self.exists_with_wd_item()
            if not item:
                item = self.exists_with_monument_article(
                    self.mapping["language"])
            if item and self.in_known_items(item):
                self.upload = False
                self.add_to_report("item_conflict", item)
            elif utils.is_blacklisted_P31(item, self.repo, disallowed):
                # the matched item is blacklisted remove match
                item = None
            else:
                self.add_to_known_items(item, mapping)
        return item

    def add_to_known_items(self, item, mapping):
        """Add the item to the list of existing items with unique property."""
        unique_prop = mapping.get_unique_prop()
        base = self.wd_item["statements"]
        if unique_prop in base:
            unique_prop_value = base[unique_prop][0]['value']
            self.existing[unique_prop_value] = item

    def construct_wd_item(self, mapping, data_files=None):
        """Create the empty structure of the data object."""
        self.wd_item = {}
        self.wd_item["upload"] = True
        self.wd_item["statements"] = {}
        self.wd_item["labels"] = {}
        self.wd_item["aliases"] = {}
        self.wd_item["descriptions"] = {}
        self.wd_item["disambiguators"] = {}
        self.wd_item["wd-item"] = None
        self.mapping = mapping.file_content

    def print_datafiles_titles(self):
        """Print out the keys in self.data_files."""
        for title in self.data_files:
            print(title)

    def get_fields(self):
        """Get a sorted list of all the attributes of the data object."""
        return sorted(list(self.__dict__.keys()))

    def add_to_report(self, key_name, raw_data, prop_name=None):
        """
        Add data to problem report json.

        Check if item has an associated Q-number,
        and if that's the case and it's missing
        in the report,
        add it to the report automatically.
        Add direct URL to item in WLM API.
        Optionally, assign a Property ID that the data
        should have been used as a value for.

        :param key_name: name of the field containing
                         the problematic data, e.g. the header of the column
        :type key_name: string
        :param raw_data: the data that we failed to process
        :type raw_data: string
        :param prop_name: name of the property,
                          as stated in the props library file
        :type prop_name: string
        """
        prop = None
        if prop_name:
            prop = self.props.get(prop_name)
        self.problem_report[key_name] = {"value": raw_data,
                                         "target": prop}
        if "wd-item" not in self.problem_report:
            if self.wd_item["wd-item"] is not None:
                self.problem_report["Q"] = self.wd_item["wd-item"]
            else:
                self.problem_report["Q"] = ""
        if "url" not in self.problem_report:
            self.problem_report["url"] = self.wlm_url

    def print_report(self):
        """Print the problem report on screen."""
        print(
            json.dumps(self.problem_report,
                       sort_keys=True,
                       indent=4,
                       ensure_ascii=False,
                       default=utils.datetime_convert)
        )

    def get_report(self):
        """Retrieve the problem report."""
        return self.problem_report


class Dataset(object):
    """A collection of Monum ents of the same type."""

    def __init__(self, country, language, monument_class):
        """
        Initialise a dataset.

        :param country: Country/Dataset code of the dataset.
        :param language: Language code of the dataset.
        :param monument_class: the sub-class of Monument to use.
        """
        self.country = country
        self.language = language
        self.monument_class = monument_class
        self.data_files = {}
        self.subclass_downloads = None
        self.lookup_downloads = None

    @property
    def table_name(self):
        """Return the expected database table name for the dataset."""
        return "monuments_{}_({})".format(self.country, self.language)

    @property
    def mapping_file(self):
        """Return the expected mapping file name for the dataset."""
        return "{}_({}).json".format(self.country, self.language)
