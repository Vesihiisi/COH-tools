from os import path
import json
from importer_utils import *


MAPPING_DIR = "mappings"
ADM0 = load_json(path.join(MAPPING_DIR, "adm0.json"))
PROPS = load_json(path.join(MAPPING_DIR, "props_general.json"))


class Monument(object):

    def print_wd(self):
        print(
            json.dumps(self.wd_item,
                       sort_keys=True,
                       indent=4,
                       ensure_ascii=False,
                       default=datetime_convert)
        )

    def add_statement(self, prop_name, value, quals={}, refs=[]):
        """
        If prop already exists, this will append another value to the array,
        i.e. two statements with the same prop.
        """
        base = self.wd_item["statements"]
        prop = PROPS[prop_name]
        qualifiers = {}
        if prop not in base:
            base[prop] = []
        if len(quals) > 0:
            for k in quals:
                prop_name = PROPS[k]
                qualifiers[prop_name] = quals[k]
        statement = {"value": value, "quals": qualifiers, "refs": refs}
        base[prop].append(statement)

    def substitute_statement(self, prop_name, value, quals={}, refs=[]):
        """
        Instead of adding to the array, replace the statement.
        This is so that instances of child classes
        can override default values...
        For example p31 museum -> art museum
        """
        base = self.wd_item["statements"]
        prop = PROPS[prop_name]
        qualifiers = {}
        if prop not in base:
            base[prop] = []
            self.add_statement(prop_name, value, quals, refs)
        else:
            if len(quals) > 0:
                for k in quals:
                    prop_name = PROPS[k]
                    qualifiers[prop_name] = quals[k]
            statement = {"value": value, "quals": qualifiers, "refs": refs}
            base[prop] = [statement]

    def add_label(self, language, text):
        base = self.wd_item["labels"]
        base[language] = text

    def add_description(self, language, text):
        base = self.wd_item["descriptions"]
        base[language] = text

    def remove_claim(self, prop):
        base = self.wd_item["statements"]
        del base[PROPS[prop]]

    def set_country(self):
        country = [item["item"]
                   for item in ADM0 if item["code"].lower() == self.adm0][0]
        self.add_statement("country", country)

    def set_is(self, mapping):
        default_is = mapping.file_content["default_is"]
        self.add_statement("is", default_is["item"])

    def set_labels(self):
        self.add_label(self.lang, remove_markup(self.name))

    def set_heritage(self, mapping):
        heritage = mapping.file_content["heritage"]
        self.add_statement("heritage_status", heritage["item"])

    def set_coords(self):
        if self.lat and self.lon:
            self.add_statement("coordinates", (self.lat, self.lon))

    def set_image(self):
        if self.image:
            self.add_statement("image", self.image)

    def set_commonscat(self):
        if self.commonscat:
            self.add_statement("commonscat", self.commonscat)

    def set_registrant_url(self):
        if self.registrant_url:
            self.wd_item["registrant_url"] = self.registrant_url

    def set_street_address(self):
        """
        NOTE: P:located at street address says
        "Include building number through to post code"
        In most cases, there's no post code in the data!
        In practice though, it's often omitted....
        Compare with located on street (P669)
        and its qualifier street number (P670).
        """
        if self.address:
            processed_address = get_street_address(self.address, self.lang)
            if processed_address is not None:
                self.add_statement("located_street", processed_address)

    def exists(self, mapping):
        self.wd_item["wd-item"] = None
        if self.monument_article:
            wd_item = q_from_wikipedia(self.lang, self.monument_article)
            self.wd_item["wd-item"] = wd_item

    def set_changed(self):
        if self.changed:
            self.wd_item["changed"] = self.changed

    def set_source(self):
        if self.source:
            self.wd_item["source"] = self.source

    def construct_wd_item(self, mapping, data_files=None):
        self.wd_item = {}
        self.wd_item["statements"] = {}
        self.wd_item["labels"] = {}
        self.wd_item["descriptions"] = {}
        self.set_labels()
        self.set_country()
        self.set_is(mapping)
        self.set_heritage(mapping)
        self.set_coords()
        self.set_image()
        self.set_commonscat()
        self.set_street_address()
        self.set_registrant_url()
        self.set_changed()
        self.set_source()
        self.exists(mapping)

    def __init__(self, db_row_dict, mapping, data_files):
        for k, v in db_row_dict.items():
            if not k.startswith("m_spec."):
                setattr(self, k.replace("-", "_"), v)
        self.construct_wd_item(mapping)
        self.data_files = data_files

    def get_fields(self):
        return sorted(list(self.__dict__.keys()))


class SeFornminSv(Monument):

    def update_labels(self):
        if len(self.namn) == 0:
            self.add_label(self.lang, self.raa_nr)
        else:
            self.add_label(self.lang, self.namn)

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
        if self.adm2 == "Göteborg":
            municip_name = "Gothenburg"
        else:
            municip_name = self.adm2
        pattern = municip_name.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "en"].lower() == pattern][0]
            self.add_statement("located_adm", municipality)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.adm2))
            return

    def set_type(self):
        """
        Replace the original P31 rather than adding to it.
        """
        if self.typ:
            table = self.data_files["types"]["mappings"]
            type_to_search_for = self.typ.lower()
            try:
                special_type = [table[x]["items"]
                                for x in table
                                if x.lower() == type_to_search_for][0]
                self.substitute_statement("is", special_type)
            except IndexError:
                return

    def get_socken(self):
        if self.socken:
            return socken_to_q(self.socken, self.landskap)

    def set_location(self):
        if self.address:
            if "[[" in self.address:
                wikilinks = get_wikilinks(self.address)
                if len(wikilinks) == 1:
                    target_page = wikilinks[0].title
                    wd_item = q_from_wikipedia(self.lang, target_page)
                    self.add_statement("location", wd_item)
        if self.socken:
            self.add_statement("location", self.get_socken())

    def set_inception(self):
        # TODO
        # This is messy and not super prioritized...
        return

    def update_wd_item(self):
        self.update_labels()
        self.set_descriptions()
        self.set_raa()
        self.set_adm_location()
        self.set_type()
        self.set_location()
        self.set_inception()

    def __init__(self, db_row_dict, mapping, data_files):
        Monument.__init__(self, db_row_dict, mapping, data_files)
        self.update_wd_item()


class SeArbetslSv(Monument):

    def update_labels(self):
        return

    def set_descriptions(self):
        DESC_BASES = {"sv": "arbetslivsmuseum", "en": "museum"}
        for language in ["en", "sv"]:
            self.add_description(language, DESC_BASES[language])

    def add_location_to_desc(self, language, municipality):
        if language == "sv":
            self.wd_item["descriptions"][language] += " i " + municipality
        elif language == "en":
            self.wd_item["descriptions"][
                language] += " in " + municipality + ", Sweden"

    def set_adm_location(self):
        municip_dict = self.data_files["municipalities"]
        if self.adm2 == "Göteborg":
            municip_name = "Gothenburg"
        else:
            municip_name = self.adm2
        pattern = municip_name.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "en"].lower() == pattern][0]
            self.add_statement("located_adm", municipality)
            swedish_name = [x["sv"]
                            for x in municip_dict
                            if x["item"] == municipality][0]
            english_name = [x["en"]
                            for x in municip_dict
                            if x["item"] == municipality][0]
            self.add_location_to_desc("sv", swedish_name)
            self.add_location_to_desc("en", english_name)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.adm2))
            return

    def set_type(self):
        if self.typ:
            table = self.data_files["types"]["mappings"]
            type_to_search_for = self.typ.lower()
            try:
                special_type = [table[x]["items"]
                                for x in table
                                if x.lower() == type_to_search_for][0]
                self.substitute_statement("is", special_type)
            except IndexError:
                return
        return

    def set_location(self):
        settlements_dict = self.data_files["settlements"]
        if self.ort:
            try:
                location = [x["item"] for x in settlements_dict if x[
                    "sv"].strip() == remove_markup(self.ort)][0]
                self.add_statement("location", location)
            except IndexError:
                # print("Could not find ort: " + self.ort)
                return

    def set_id(self):
        if self.id:
            self.add_statement("arbetsam", self.id)

    def update_wd_item(self):
        self.update_labels()
        self.set_descriptions()
        self.set_id()
        self.set_adm_location()
        self.set_type()
        self.set_location()

    def __init__(self, db_row_dict, mapping, data_files=None):
        Monument.__init__(self, db_row_dict, mapping, data_files)
        self.update_wd_item()


class SeShipSv(Monument):

    """
    TODO
    * handle material (from lookup table)
    * handle function (from lookup table)
    """

    def update_labels(self):
        return

    def set_shipyard(self):
        if self.varv:
            possible_varv = self.varv
            if "<br>" in possible_varv:
                possible_varv = self.varv.split("<br>")[0]
            if "[[" in possible_varv:
                varv = q_from_first_wikilink("sv", possible_varv)
                self.add_statement("manufacturer", varv)

    def set_manufacture_year(self):
        """
        TODO
        !!!!!
        add "year" etc. so that it can be processed by pywikibot
        See:
        """
        if self.byggar:
            byggar = parse_year(remove_characters(self.byggar, ".,"))
            self.add_statement("inception", {"time_value": byggar})

    def set_dimensions(self):
        if self.dimensioner:
            dimensions_processed = parse_ship_dimensions(self.dimensioner)
            for dimension in dimensions_processed:
                if dimension in PROPS:
                    value = dimensions_processed[dimension]
                    self.add_statement(
                        dimension, {"quantity_value": value,
                                    "unit": PROPS["metre"]})

    def set_homeport(self):
        if self.hemmahamn and count_wikilinks(self.hemmahamn) == 1:
            home_port = q_from_first_wikilink("sv", self.hemmahamn)
            self.add_statement("home_port", home_port)

    def set_call_sign(self):
        if self.signal:
            self.add_statement("call_sign", self.signal)

    def update_wd_item(self):
        self.update_labels()
        self.set_manufacture_year()
        self.set_shipyard()
        self.set_homeport()
        self.set_dimensions()
        self.set_call_sign()

    def __init__(self, db_row_dict, mapping, data_files=None):
        Monument.__init__(self, db_row_dict, mapping, data_files)
        self.update_wd_item()


class SeBbrSv(Monument):

    def update_labels(self):
        """
        TODO
        Original labels look like this:
            Wickmanska gården (Paradis 35)
        We don't need the latter part (fastighetsbeteckning) in the label,
        but it's important info to have.
        What's the best place for it?
        Have a look at https://www.wikidata.org/wiki/Property_talk:P528
        for now, we'll just put them in the description field!

        wtf is "K 0188"???
        """
        self.add_label("sv", get_rid_of_brackets(self.wd_item["labels"]["sv"]))
        return

    def set_bbr(self):
        """
        TODO
        check if there are items with no BBR
        """
        bbr_link = get_bbr_link(self.bbr)
        self.add_statement("bbr", bbr_link)

    def set_heritage_bbr(self):
        """
        TODO: Get starts_from from parentheses in
        byggnadsminne and statligt byggnadsminne.
        This needs to be overriden from parent class,
        because there are three possible options that can't be
        mapped automatically:
        ---
        In Sweden there are three different types of legal protection
        for different types of cultural heritage,
        so we created three new items:

        governmental listed building complex (Q24284071)
        for buildings owned by the state,

        individual listed building complex (Q24284072)
        for privately owned buildings,

        ecclesiastical listed building complex (Q24284073)
        for older buildings owned by the Church of Sweden.

        Which legal protection each monument goes under
        is not stored in the WLM database.
        We therefore need to look that up by
        querying the source database via their API.
        """
        # print(self.wd_item["statements"][PROPS["heritage_status"]])
        url = "http://kulturarvsdata.se/" + \
            self.wd_item["statements"][PROPS["bbr"]][0]["value"]
        url_list = url.split("/")
        url_list.insert(-1, "jsonld")
        url = "/".join(url_list)
        data = requests.get(url).json()
        for element in data["@graph"]:
            if "ns5:spec" in element:
                bbr_type = element["ns5:spec"]
                if bbr_type.startswith("Kyrkligt kulturminne"):
                    type_q = "Q24284073"
                elif bbr_type.startswith("Byggnadsminne"):
                    type_q = "Q24284072"
                elif bbr_type.startswith("Statligt byggnadsminne"):
                    type_q = "Q24284071"
        """
        The original set_heritage() added an empty claim
        because there's no heritage status specified in mapping file,
        so we start by removing that empty claim.
        """
        self.remove_claim("heritage_status")
        self.add_statement("heritage_status", type_q)

    def set_function(self):
        """
        TODO
        Isolate function and number of buildings:
            Kyrka sammanbyggd med församlingshem (1 byggnad)
            Slott (4 byggnader)
            Gästgivargård (1 byggnad)
        """
        return

    def set_architect(self):
        if self.arkitekt:
            architects = get_wikilinks(self.arkitekt)
            for name in architects:
                wp_page = name.title
                q_item = q_from_wikipedia("sv", wp_page)
                if q_item is not None:
                    self.add_statement("architect", q_item)

    def set_location(self):
        """
        TODO
        This is the same as 'address' in monuments_all.
        There are some street addresses. Some are simple:
            Norra Murgatan 3
        Some are complex:
            Skolgatan 5, Västra Kyrkogatan 3
            Norra Murgatan 27, Uddens gränd 14-16
        """
        if self.plats:
            if count_wikilinks(self.plats) == 1:
                location = q_from_first_wikilink(self.lang, self.plats)
                self.add_statement("location", location)
            # TODO: process if no wikilinks
        return

    def update_descriptions(self):
        fastighetsbeteckning = get_text_inside_brackets(self.name)
        self.add_description("sv", fastighetsbeteckning)

    def set_no_of_buildings(self):
        """
        Most common value of type:
            4 byggnader
        However, there are also items like
            inga registrerade byggnader
            Livsmedelsindustri, Tobak och snus
        """
        extracted_no = get_number_from_string(
            get_text_inside_brackets(self.funktion))
        if extracted_no is not None:
            self.add_statement(
                "has_parts_of_class", "Q41176", {"quantity": extracted_no})

    def set_adm_location(self):
        if self.adm2 == "Göteborg":
            municip_name = "Gothenburg"
        else:
            municip_name = self.adm2
        municip_dict = load_json(path.join(
            MAPPING_DIR, "sweden_municipalities.json"))
        pattern_en = municip_name.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "en"].lower() == pattern_en][0]
            self.add_statement("located_adm", municipality)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.adm2))
            return

    def set_inception(self):
        """
        TODO
        Some fun examples:
            1800-1809 <- this should work
            1314 <- this too
            1800-talets början <- hmmmm
            1700-talet <- this should work! have a look at precision
        """
        if self.byggar:
            return

    def update_wd_item(self):
        self.update_labels()
        self.update_descriptions()
        # self.set_bbr()
        # self.set_heritage_bbr()
        self.set_function()
        self.set_architect()
        self.set_location()
        self.set_adm_location()
        self.set_no_of_buildings()
        self.set_inception()

    def __init__(self, db_row_dict, mapping, data_files=None):
        Monument.__init__(self, db_row_dict, mapping, data_files)
        self.update_wd_item()


class DkBygningDa(Monument):

    def update_wd_item(self):
        print(self.name)

    def __init__(self, db_row_dict, mapping, data_files=None):
        Monument.__init__(self, db_row_dict, mapping, data_files)
        self.update_wd_item()
