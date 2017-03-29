from os import path
import json
import importer_utils as utils

MAPPING_DIR = "mappings"


class Monument(object):

    def print_wd(self):
        """Print the data object dictionary on screen."""
        print(
            json.dumps(self.wd_item,
                       sort_keys=True,
                       indent=4,
                       ensure_ascii=False,
                       default=utils.datetime_convert)
        )

    def print_wd_to_table(self):
        """Generate a wikitext preview table of the data item."""
        table = ""
        labels = self.wd_item["labels"]
        descriptions = self.wd_item["descriptions"]
        aliases = self.wd_item["aliases"]
        table = table + "'''Labels'''\n\n"
        for l in labels:
            table = table + "* '''" + l + "''': " + labels[l] + "\n\n"
        table = table + "'''Descriptions'''\n\n"
        for d in descriptions:
            table = table + "* '''" + d + "''': " + descriptions[d] + "\n\n"
        table = table + "'''Aliases'''\n\n"
        for a in aliases:
            for single_alias in aliases[a]:
                table = table + "* '''" + a + "''': " + single_alias + "\n\n"
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
                value_to_print = ""
                if utils.string_is_q_item(value):
                    value = utils.wd_template("Q", value)
                    value_to_print += str(value)
                elif "quantity_value" in value:
                    value_to_print += str(value["quantity_value"])
                    if "unit" in value:
                        value_to_print += " " + utils.wd_template("Q", value["unit"])
                elif "time_value" in value:
                    value_to_print += utils.dict_to_iso_date(value["time_value"])
                else:
                    value_to_print += str(value)
                quals = claim["quals"]
                refs = claim["refs"]
                if len(quals) == 0:
                    qual_to_print = ""
                else:
                    for q in quals:
                        qual_to_print = utils.wd_template(
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
                table = table + "| " + qual_to_print + "\n"
                table = table + "| " + ref_to_print + "\n"
        table = table + "|}\n"
        table = table + "----------\n"
        return table

    def add_statement(self, prop_name, value, quals=None, refs=None):
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

        :param prop_name: name of the property, as stated in the props library file
        :param value: the value of the property
        :param quals: a dictionary of qualifiers
        :param refs: a list of references or a single reference.
            Set None/True for the default reference, set False to not add a reference.
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
            refs = None

        if refs and not isinstance(refs, list):
            refs = [refs]
        statement = {"value": value, "quals": qualifiers, "refs": refs}
        base[prop].append(statement)

    def remove_statement(self, prop_name):
        """
        Remove all statements with a given property from the data object.

        :param prop_name: name of the property, as stated in the props library file
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

    def set_country(self):
        """Set the country using the mapping file."""
        code = self.mapping["country_code"].lower()
        country = [item["item"]
                   for item in self.adm0 if item["code"].lower() == code][0]
        self.add_statement("country", country)

    def set_is(self):
        """Set the P31 property using the mapping file."""
        default_is = self.mapping["default_is"]
        self.add_statement("is", default_is["item"])

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

    def set_coords(self, coord_keywords_tuple):
        """
        Add coordinates.

        :param coord_keywords_tuple: names of the columns with
            coordinates, like ("lat", "long")
        """
        lat = coord_keywords_tuple[0]
        lon = coord_keywords_tuple[1]
        if self.has_non_empty_attribute(lat):
            if self.lat == 0 and self.lon == 0:
                return
            else:
                latitude = getattr(self, lat)
                longitude = getattr(self, lon)
                self.add_statement(
                    "coordinates", (latitude, longitude))

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

    def has_non_empty_attribute(self, attr_name):
        """
        Check whether the data object has has an attribute and it's
        not an empty string.

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

    def exists(self, language, article_keyword="monument_article"):
        if self.has_non_empty_attribute(article_keyword):
            wd_item = utils.q_from_wikipedia(
                language, getattr(self, article_keyword))
            self.set_wd_item(wd_item)

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

    def exists_with_prop(self, mapping):
        if self.existing is None:
            return
        unique_prop = mapping.get_unique_prop()
        base = self.wd_item["statements"]
        if unique_prop in base:
            val_to_check = base[unique_prop][0]['value']
            if val_to_check in self.existing:
                wd_item = self.existing[val_to_check]
                print("Wikidata has item with {} = {}. Connecting with item {}.".format(
                    unique_prop, val_to_check, wd_item))
                # Check whether it already has self.wd_item
                # from monument_article.
                # This of course assumes that self.exist is run earlier.
                # If it's a different one,
                wd_item_from_monument_article = self.wd_item["wd-item"]
                if wd_item != wd_item_from_monument_article:
                    # different Q-numbers from monuments_all and
                    # unique property
                    self.wd_item["upload"] = False
                else:
                    pass  # match
                self.set_wd_item(wd_item)
            else:
                print("There's no item with {} = {} on Wikidata.".format(
                    unique_prop, val_to_check))

    def construct_wd_item(self, mapping, data_files=None):
        """Create the empty structure of the data object."""
        self.wd_item = {}
        self.wd_item["upload"] = True
        self.wd_item["statements"] = {}
        self.wd_item["labels"] = {}
        self.wd_item["aliases"] = {}
        self.wd_item["descriptions"] = {}
        self.wd_item["wd-item"] = None
        self.mapping = mapping.file_content

    def print_datafiles_titles(self):
        """Print out the keys in self.data_files."""
        for title in self.data_files:
            print(title)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        self.props = utils.load_json(
            path.join(MAPPING_DIR, "props_general.json"))
        self.common_items = utils.load_json(
            path.join(MAPPING_DIR, "common_items.json"))
        self.adm0 = utils.load_json(path.join(MAPPING_DIR, "adm0.json"))
        self.sources = utils.load_json(
            path.join(MAPPING_DIR, "data_sources.json"))
        for k, v in db_row_dict.items():
            if not k.startswith("m_spec."):
                setattr(self, k.replace("-", "_"), v)
        self.monuments_all_id = ""
        self.construct_wd_item(mapping)
        self.data_files = data_files
        self.existing = existing
        self.problem_report = {}

    def get_fields(self):
        """Get a sorted list of all the attributes of the data object."""
        return sorted(list(self.__dict__.keys()))

    def add_to_report(self, key_name, raw_data):
        """
        Add data to problem report json.

        Check if item has an associated Q-number,
        and if that's the case and it's missing
        in the report,
        add it to the report automatically.
        Add direct URL to item in WLM API.
        """
        self.problem_report[key_name] = raw_data
        if "wd-item" not in self.problem_report:
            if self.wd_item["wd-item"] is not None:
                self.problem_report["Q"] = self.wd_item["wd-item"]
            else:
                self.problem_report["Q"] = ""
        if "url" not in self.problem_report:
            self.problem_report["url"] = self.wlm_url

    def print_report(self):
        """
        Print the problem report on screen.
        """
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
