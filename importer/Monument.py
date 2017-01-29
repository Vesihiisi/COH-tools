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
        if len(quals) > 0:
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
        qualifiers = {}
        if prop not in base:
            base[prop] = []
            self.add_statement(prop_name, value, quals, refs)
        else:
            if len(quals) > 0:
                for k in quals:
                    prop_name = self.props[k]
                    qualifiers[prop_name] = quals[k]
            statement = {"value": value, "quals": qualifiers, "refs": refs}
            base[prop] = [statement]

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

    def remove_claim(self, prop):
        base = self.wd_item["statements"]
        del base[self.props[prop]]

    def set_country(self, mapping):
        code = mapping.file_content["country_code"].lower()
        country = [item["item"]
                   for item in self.adm0 if item["code"].lower() == code][0]
        self.add_statement("country", country)

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
                self.add_statement(
                    "coordinates", (getattr(self, lat), getattr(self, lon)))

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
            processed_address = get_street_address(
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

    def exists_with_prop(self, mapping):
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
        self.set_country(mapping)
        self.set_is(mapping)
        self.set_heritage(mapping)
        self.set_source()
        self.set_registrant_url()
        self.set_changed()

    def __init__(self, db_row_dict, mapping, data_files, existing):
        self.props = utils.load_json(
            path.join(MAPPING_DIR, "props_general.json"))
        self.adm0 = utils.load_json(path.join(MAPPING_DIR, "adm0.json"))
        for k, v in db_row_dict.items():
            if not k.startswith("m_spec."):
                setattr(self, k.replace("-", "_"), v)
        self.construct_wd_item(mapping)
        self.data_files = data_files
        self.existing = existing
        print(".........................................")

    def get_fields(self):
        return sorted(list(self.__dict__.keys()))


class SeFornminSv(Monument):

    def update_labels(self):
        if len(self.namn) == 0:
            self.add_label("sv", self.raa_nr)
        else:
            self.add_label("sv", self.namn)

    def set_descriptions(self):
        """
        """
        DESC_BASE = "fornminne"
        description = ""
        if len(self.typ) > 0:
            description = self.typ.lower()
        else:
            description = DESC_BASE
        description += " i " + self.landskap
        self.add_description("sv", description)

    def set_raa(self):
        """
        With registrant_url as source, to test source uploading mechanism
        """
        self.add_statement("raa-nr", self.raa_nr, refs=[self.registrant_url])

    def set_adm_location(self):
        municip_dict = load_json(path.join(
            MAPPING_DIR, "sweden_municipalities.json"))
        if self.kommun == "Göteborg":
            municip_name = "Gothenburg"
        else:
            municip_name = self.kommun
        pattern = municip_name.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "en"].lower() == pattern][0]
            self.add_statement("located_adm", municipality)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.kommun))
            return

    def set_type(self):
        """
        Replace the original P31 rather than adding to it.
        """
        if self.has_non_empty_attribute("typ"):
            table = self.data_files["types"]["mappings"]
            type_to_search_for = self.typ.lower()
            try:
                special_type = [table[x]["items"]
                                for x in table
                                if x.lower() == type_to_search_for][0]
                self.substitute_statement("is", special_type)
            except IndexError:
                return

    def get_socken(self, socken_name, landskap_name):
        return socken_to_q(socken_name, landskap_name)

    def set_location(self):
        if self.has_non_empty_attribute("plats"):
            if "[[" in self.plats:
                wikilinks = get_wikilinks(self.address)
                if len(wikilinks) == 1:
                    target_page = wikilinks[0].title
                    wd_item = q_from_wikipedia(self.lang, target_page)
                    self.add_statement("location", wd_item)
        if self.has_non_empty_attribute("socken"):
            self.add_statement("location", self.get_socken(
                self.socken, self.landskap))

    def set_inception(self):
        # TODO
        # This is messy and not super prioritized...
        return

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.set_image("bild")
        self.update_labels()
        self.set_descriptions()
        self.set_raa()
        self.set_adm_location()
        self.set_type()
        self.set_location()
        self.set_inception()
        # self.exists("sv", "artikel")
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
        # self.exists_with_prop(mapping)
        # self.print_wd()


