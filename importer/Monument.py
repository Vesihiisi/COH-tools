from os import path
import json
import importer_utils as utils


MAPPING_DIR = "mappings"


class Monument(object):

    def print_wd(self):
        print(
            json.dumps(self.wd_item,
                       sort_keys=True,
                       indent=4,
                       ensure_ascii=False,
                       default=utils.datetime_convert)
        )

    def print_wd_to_table(self):
        """
        {| class="wikitable"
        |-
        ! Header C1
        ! Header C2
        ! Header C3
        |-
        | R1C1
        | R1C2
        | R1C3
        |-
        | R2C1
        | R2C2
        | R2C3
        |}
        """
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
                value_to_print = value_to_print + str(value)
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
                        ref_to_print = str(r)
                table = table + "|-\n"
                table = table + "| " + utils.wd_template("P", statement) + "\n"
                table = table + "| " + value_to_print + "\n"
                table = table + "| " + qual_to_print + "\n"
                table = table + "| " + ref_to_print + "\n"
        table = table + "|}\n"
        table = table + "----------\n"
        return table

    def add_statement(self, prop_name, value, quals={}, refs=[]):
        """
        If prop already exists, this will append another value to the array,
        i.e. two statements with the same prop.
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
        statement = {"value": value, "quals": qualifiers, "refs": refs}
        base[prop].append(statement)

    def remove_statement(self, prop_name):
        base = self.wd_item["statements"]
        prop = self.props[prop_name]
        if prop in base:
            del base[prop]

    def substitute_statement(self, prop_name, value, quals={}, refs=[]):
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
        if wd_item is not None:
            self.wd_item["wd-item"] = wd_item
            print("Associated WD item: ", wd_item)

    def add_label(self, language, text):
        base = self.wd_item["labels"]
        base[language] = text

    def add_alias(self, language, text):
        base = self.wd_item["aliases"]
        if language not in base:
            base[language] = []
        base[language].append(text)

    def add_description(self, language, text):
        base = self.wd_item["descriptions"]
        base[language] = text

    def set_country(self, mapping):
        code = mapping.file_content["country_code"].lower()
        country = [item["item"]
                   for item in self.adm0 if item["code"].lower() == code][0]
        ref = self.create_wlm_source()
        self.add_statement("country", country, refs=[ref])

    def set_is(self, mapping):
        default_is = mapping.file_content["default_is"]
        self.add_statement("is", default_is["item"])

    def set_labels(self, language, content):
        self.add_label(language, utils.remove_markup(content))

    def set_heritage(self, mapping):
        heritage = mapping.file_content["heritage"]
        self.add_statement("heritage_status", heritage["item"])

    def set_coords(self, coord_keywords_tuple):
        lat = coord_keywords_tuple[0]
        lon = coord_keywords_tuple[1]
        if self.has_non_empty_attribute(lat):
            if self.lat == 0 and self.lon == 0:
                return
            else:
                ref = self.create_wlm_source()
                self.add_statement(
                    "coordinates", (getattr(self, lat), getattr(self, lon)), refs=[ref])

    def set_image(self, image_keyword="image"):
        if self.has_non_empty_attribute(image_keyword):
            self.add_statement("image", getattr(self, image_keyword))

    def set_commonscat(self, keyword="commonscat"):
        if self.has_non_empty_attribute(keyword):
            self.add_statement("commonscat", getattr(self, keyword))

    def set_registrant_url(self):
        if self.has_non_empty_attribute("registrant_url"):
            self.wd_item["registrant_url"] = self.registrant_url

    def set_street_address(self, language, address_keyword):
        """
        NOTE: P:located at street address says
        "Include building number through to post code"
        In most cases, there's no post code in the data!
        In practice though, it's often omitted....
        Compare with located on street (P669)
        and its qualifier street number (P670).
        """
        if self.has_non_empty_attribute(address_keyword):
            processed_address = utils.get_street_address(
                getattr(self, address_keyword), language)
            if processed_address is not None:
                self.add_statement("located_street", processed_address)

    def has_non_empty_attribute(self, attr_name):
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
        if self.changed:
            self.wd_item["changed"] = self.changed

    def set_source(self):
        if self.has_non_empty_attribute("source"):
            self.wd_item["source"] = self.source

    def create_stated_in_source(self, source_item, pub_date):
        prop_stated = self.props["stated_in"]
        prop_date = self.props["publication_date"]
        return {"source": {"prop": prop_stated, "value": source_item},
                "published": {"prop": prop_date, "value": pub_date}}

    def create_wlm_source(self):
        source_item = self.sources["monuments_db"]
        timestamp = self.wd_item["changed"]
        return self.create_stated_in_source(source_item, timestamp)

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
                self.set_wd_item(wd_item)
            else:
                print("There's no item with {} = {} on Wikidata.".format(
                    unique_prop, val_to_check))

    def construct_wd_item(self, mapping, data_files=None):
        self.wd_item = {}
        self.wd_item["statements"] = {}
        self.wd_item["labels"] = {}
        self.wd_item["aliases"] = {}
        self.wd_item["descriptions"] = {}
        self.wd_item["wd-item"] = None
        self.set_changed()
        self.set_country(mapping)
        self.set_is(mapping)
        self.set_heritage(mapping)
        self.set_source()
        self.set_registrant_url()

    def __init__(self, db_row_dict, mapping, data_files, existing):
        self.props = utils.load_json(
            path.join(MAPPING_DIR, "props_general.json"))
        self.adm0 = utils.load_json(path.join(MAPPING_DIR, "adm0.json"))
        self.sources = utils.load_json(
            path.join(MAPPING_DIR, "data_sources.json"))
        for k, v in db_row_dict.items():
            if not k.startswith("m_spec."):
                setattr(self, k.replace("-", "_"), v)
        self.construct_wd_item(mapping)
        self.data_files = data_files
        self.existing = existing

    def get_fields(self):
        return sorted(list(self.__dict__.keys()))
