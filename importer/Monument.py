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

    def remove_statement(self, prop_name):
        base = self.wd_item["statements"]
        prop = PROPS[prop_name]
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
        del base[PROPS[prop]]

    def set_country(self, mapping):
        code = mapping.file_content["country_code"].lower()
        country = [item["item"]
                   for item in ADM0 if item["code"].lower() == code][0]
        self.add_statement("country", country)

    def set_is(self, mapping):
        default_is = mapping.file_content["default_is"]
        self.add_statement("is", default_is["item"])

    def set_labels(self, language, content):
        self.add_label(language, remove_markup(content))

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
            wd_item = q_from_wikipedia(
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
                print("Wikidata has item with {} = {}. Connecting with item {}.".format(unique_prop, val_to_check, wd_item))
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
        self.set_country(mapping)
        self.set_is(mapping)
        self.set_heritage(mapping)
        self.set_source()
        self.set_registrant_url()
        self.set_changed()

    def __init__(self, db_row_dict, mapping, data_files, existing):
        for k, v in db_row_dict.items():
            if not k.startswith("m_spec."):
                setattr(self, k.replace("-", "_"), v)
        self.construct_wd_item(mapping)
        self.data_files = data_files
        self.existing = existing

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
        self.exists_with_prop(mapping)
        # self.print_wd()


class SeArbetslSv(Monument):

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
        if self.kommun == "Göteborg":
            municip_name = "Gothenburg"
        else:
            municip_name = self.kommun
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
            print("Could not parse municipality: {}.".format(self.kommun))
            return

    def set_type(self):
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
        return

    def set_location(self):
        settlements_dict = self.data_files["settlements"]
        if self.has_non_empty_attribute("ort"):
            try:
                location = [x["item"] for x in settlements_dict if x[
                    "sv"].strip() == remove_markup(self.ort)][0]
                self.add_statement("location", location)
            except IndexError:
                return

    def set_id(self):
        if self.has_non_empty_attribute("id"):
            self.add_statement("arbetsam", self.id)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.set_labels("sv", self.namn)
        self.set_descriptions()
        self.set_id()
        self.set_type()
        self.set_adm_location()
        self.set_location()
        self.exists("sv", "monument_article")
        self.set_image("bild")
        self.set_commonscat()
        self.set_coords(("lat", "lon"))
        self.exists_with_prop(mapping)
        # self.print_wd()


class SeShipSv(Monument):

    """
    TODO
    * handle material (from lookup table)
    """

    def set_type(self):
        table = self.data_files["functions"]["mappings"]
        if self.funktion:
            special_type = self.funktion.lower()
            try:
                functions = [table[x]["items"]
                             for x in table if x.lower() == special_type][0]
                if len(functions) > 0:
                    self.remove_statement("is")
                    for f in functions:
                        self.add_statement("is", f)
            except IndexError:
                return

    def set_shipyard(self):
        if self.has_non_empty_attribute("varv"):
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
        if self.has_non_empty_attribute("byggar"):
            byggar = parse_year(remove_characters(self.byggar, ".,"))
            self.add_statement("inception", {"time_value": byggar})

    def set_dimensions(self):
        if self.has_non_empty_attribute("dimensioner"):
            dimensions_processed = parse_ship_dimensions(self.dimensioner)
            for dimension in dimensions_processed:
                if dimension in PROPS:
                    value = dimensions_processed[dimension]
                    self.add_statement(
                        dimension, {"quantity_value": value,
                                    "unit": PROPS["metre"]})

    def set_homeport(self):
        if self.has_non_empty_attribute("hemmahamn"):
            if count_wikilinks(self.hemmahamn) == 1:
                home_port = q_from_first_wikilink("sv", self.hemmahamn)
                self.add_statement("home_port", home_port)

    def set_call_sign(self):
        if self.has_non_empty_attribute("signal"):
            self.add_statement("call_sign", self.signal)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.set_labels("sv", self.namn)
        self.set_image("bild")
        self.exists("sv", "artikel")
        self.set_type()
        self.set_commonscat()
        self.set_call_sign()
        self.set_manufacture_year()
        self.set_shipyard()
        self.set_homeport()
        self.set_dimensions()
        self.exists_with_prop(mapping)
        self.print_wd()


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
        label = get_rid_of_brackets(remove_markup(self.namn))
        self.add_label("sv", label)
        return

    def set_type(self):
        return

    def set_bbr(self):
        bbr_link = get_bbr_link(self.bbr)
        self.add_statement("bbr", bbr_link)

    def set_heritage_bbr(self):
        """
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
        url = "http://kulturarvsdata.se/" + \
            self.wd_item["statements"][PROPS["bbr"]][0]["value"]
        url_list = url.split("/")
        url_list.insert(-1, "jsonld")
        url = "/".join(url_list)
        data = requests.get(url).json()
        for element in data["@graph"]:
            if "ns5:spec" in element:
                protection_date = False
                bbr_type = element["ns5:spec"]
                if bbr_type.startswith("Kyrkligt kulturminne"):
                    type_q = "Q24284073"
                elif bbr_type.startswith("Byggnadsminne"):
                    type_q = "Q24284072"
                    protection_date = bbr_type.split("(")[-1][:-1]
                elif bbr_type.startswith("Statligt byggnadsminne"):
                    type_q = "Q24284071"
                    protection_date = bbr_type.split("(")[-1][:-1]
        """
        The original set_heritage() added an empty claim
        because there's no heritage status specified in mapping file,
        so we start by removing that empty claim.
        """
        self.remove_claim("heritage_status")
        if protection_date:
            # 1969-01-31
            date_dict = date_to_dict(protection_date, "%Y-%m-%d")
            qualifier = {"start_time":
                         {"time_value": date_dict}}
        else:
            qualifier = None
        self.add_statement("heritage_status", type_q, qualifier)

    def set_function(self):
        """
        TODO
        examples:
        https://gist.github.com/Vesihiisi/f637916ea1d80a4be5d71a3adf6e2dc2
        """
        # functions = get_rid_of_brackets(self.funktion).lower().split(",")
        return

    def set_architect(self):
        if self.has_non_empty_attribute("arkitekt"):
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
        if self.has_non_empty_attribute("plats"):
            if count_wikilinks(self.plats) == 1:
                location = q_from_first_wikilink("sv", self.plats)
                self.add_statement("location", location)

    def update_descriptions(self):
        fastighetsbeteckning = get_text_inside_brackets(self.namn)
        self.add_alias("sv", fastighetsbeteckning)

    def set_no_of_buildings(self):
        extracted_no = get_number_from_string(
            get_text_inside_brackets(self.funktion))
        if extracted_no is not None:
            self.add_statement(
                "has_parts_of_class", "Q41176",
                {"quantity": {"quantity_value": extracted_no}})

    def set_adm_location(self):
        if self.kommun == "Göteborg":
            municip_name = "Gothenburg"
        else:
            municip_name = self.kommun
        municip_dict = load_json(path.join(
            MAPPING_DIR, "sweden_municipalities.json"))
        pattern_en = municip_name.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "en"].lower() == pattern_en][0]
            self.add_statement("located_adm", municipality)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.kommun))
            return

    def set_inception(self):
        if self.has_non_empty_attribute("byggar"):
            year_parsed = parse_year(self.byggar)
            if year_parsed is not None:
                self.add_statement("inception", {"time_value": year_parsed})

    def __init__(self, db_row_dict, mapping, data_files, existing):
        """
        TODO
        Add an extra check for existing article using bbr?
        not only monument_article
        """
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        self.update_descriptions()
        self.set_image("bild")
        self.exists("sv")
        self.set_commonscat()
        self.set_type()
        self.set_coords(("lat", "lon"))
        self.set_inception()
        self.set_no_of_buildings()
        self.set_bbr()
        self.set_heritage_bbr()
        self.set_adm_location()
        self.set_architect()
        self.set_location()
        self.set_function()
        self.exists_with_prop(mapping)
        # self.print_wd()


class DkBygningDa(Monument):

    def set_adm_location(self):
        if self.has_non_empty_attribute("kommune"):
            if count_wikilinks(self.kommune) == 1:
                adm_location = q_from_first_wikilink("da", self.kommune)
                self.add_statement("located_adm", adm_location)

    def set_location(self):
        """
        Use self.municipality because IT'S PLACE NOT MUNICIPALITY
        (that's adm2)
        """
        place_item = False
        if self.has_non_empty_attribute("by"):
            place = self.by
            if count_wikilinks(place) == 1:
                place_item = q_from_first_wikilink("da", place)
            else:
                if wp_page_exists("da", place):
                    place_item = q_from_wikipedia("da", place)
        if place_item:
            self.add_statement("location", place_item)

    def set_sagsnr(self):
        """
        Danish listed buildings case ID (P2783)
        """
        self.add_statement("listed_building_dk", str(self.sagsnr))

    def update_labels(self):
        self.add_label("da", remove_markup(self.sagsnavn))

    def set_address(self):
        """
        Really nice addresses in this table.
        """
        if self.has_non_empty_attribute("adresse"):
            address = self.adresse + " " + self.postnr + " " + self.by
            self.add_statement("located_street", address)

    def set_inception(self):
        if self.has_non_empty_attribute("opforelsesar"):
            inception = parse_year(self.opforelsesar)
            self.add_statement("inception", {"time_value": inception})

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        self.exists("da")
        self.set_commonscat()
        self.set_image("billede")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_location()
        self.set_sagsnr()
        self.set_address()
        self.set_inception()
        self.exists_with_prop(mapping)
        # self.print_wd()


class DkFortidsDa(Monument):

    def update_labels(self):
        """
        TODO: Naming things!
        See:
        https://da.wikipedia.org/wiki/Fredede_fortidsminder_i_Ikast-Brande_Kommune
        The monuments don't have unique names, stednavn
        is a general placename.
        Use the description field to provide better info:
        'rundhøj i Ikast-Brande kommune'
        """
        self.add_label("da", remove_markup(self.stednavn))

    def update_descriptions(self):
        monument_type = remove_markup(self.type).lower()
        municipality = remove_markup(self.kommune)
        description_da = "{} i {}".format(monument_type, municipality)
        self.add_description("da", description_da)

    def set_adm_location(self):
        if self.has_non_empty_attribute("kommune"):
            if count_wikilinks(self.kommune) == 1:
                adm_location = q_from_first_wikilink("da", self.kommune)
                self.add_statement("located_adm", adm_location)

    def set_type(self):
        if self.has_non_empty_attribute("type"):
            table = self.data_files["types"]["mappings"]
            try:
                special_type = [table[x]["items"]
                                for x in table
                                if x == self.type][0]
                self.substitute_statement("is", special_type)
            except IndexError:
                return

    def set_inception(self):
        """
        TODO
        these are very broad...
        basically "prehistoric time", "modern time"
        is this even useful?
        """
        if self.has_non_empty_attribute("datering"):
            if len(get_wikilinks(self.datering)) == 1:
                print(self.datering)
                print(q_from_first_wikilink("da", self.datering))

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        self.update_descriptions()
        self.exists("da")
        self.set_commonscat()
        self.set_image("billede")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_type()
        # self.set_inception()
        # self.set_location()
        # self.set_sagsnr()
        # self.set_address()
        # self.set_inception()
        # self.print_wd()
        self.exists_with_prop(mapping)


class NoNo(Monument):

    """
    TODO
    there's an API:
    https://data.norge.no/data/riksantikvaren/kulturminnes%C3%B8k
    look into how we can benefit from it!
    """

    def update_labels(self):
        """
        NOTE
        Some of these are in all caps or have multiple spaces:
        UTSIRA FYRSTASJON
        SØGARD FJONE  -  FJONE SØNDRE
        VÅLE PRESTEGÅRD, museum

        TODO
        *Normalize - to title case?
            It contains some old-style numbers, and these will be broken:
            XXVIII -> Xxviii

        * rm extra whitespace
        """
        for part in self.navn.split(" "):
            if part.isupper():
                print(part, "----", part.capitalize())

    def set_no(self):
        self.add_statement("norwegian_monument_id", self.id)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("no")
        self.set_commonscat()
        self.set_image("bilde")
        self.set_coords(("lat", "lon"))
        self.set_no()
        # self.set_adm_location()
        # self.set_location()
        # self.set_sagsnr()
        # self.set_address()
        # self.set_inception()
        # self.print_wd()
        self.exists_with_prop(mapping)


class EeEt(Monument):

    def update_labels(self):
        name = remove_markup(self.nimi)
        self.add_label("et", name)

    def set_no(self):
        register_no = str(self.registrant_url.split("=")[-1])
        self.add_statement("estonian_monument_id", register_no)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("et")
        self.set_commonscat()
        self.set_image("pilt")
        self.set_coords(("lat", "lon"))
        self.set_no()
        # self.set_adm_location()
        # self.set_location()
        # self.set_sagsnr()
        # self.set_address()
        # self.set_inception()
        self.exists_with_prop(mapping)
        self.print_wd()


class PlPl(Monument):

    def update_labels(self):
        name = remove_markup(self.nazwa)
        self.add_label("pl", name)

    def set_adm_location(self):
        """
        TODO
        These are not wikilinked...
        And the labels on wd are in different formats,
        sometimes with 'gmina' and sometimes without.
        How to match them correctly?
        """
        if "gmina " in self.gmina:
            municipality = self.gmina.split(" ")[1:]
            municipality = ' '.join(municipality)
        else:
            municipality = self.gmina

    def set_no(self):
        """
        TODo
        Examples of what these can look like: http://tinyurl.com/jz5vuc4
        isolate the date and use as start_time
        sometimes there are two values:
        250 z 16.08.1957, 8 z 17.02.1981 (WUOZ - A/463)
        first step: split on comma OR semicolon?
        or start by isolating the dates and work backwards
        """
        # print(self.numer)
        return

    def set_address(self):
        """
        NOTE
        Sometimes this is broken and only a number is included,
        like "70".
        But then you can't just test for if it's only number
        because sometimes it's like "70 B"
        Check for length? Min 5 characters?
        """
        if self.has_non_empty_attribute("adres") and len(self.adres) > 5:
            street = remove_markup(self.adres)
            self.add_statement("located_street", street)

    def set_location(self):
        settlements_dict = self.data_files["settlements"]
        if count_wikilinks(self.miejscowosc) == 1:
            location = q_from_first_wikilink("pl", self.miejscowosc)
            self.add_statement("location", location)
        else:
            placename = remove_markup(self.miejscowosc)
            try:
                location = [x["item"] for x in settlements_dict if x[
                    "pl"].strip() == placename][0]
                self.add_statement("location", location)
            except IndexError:
                return

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("pl")
        self.set_commonscat()
        self.set_image("zdjecie")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_no()
        self.set_location()
        # self.set_sagsnr()
        self.set_address()
        # self.set_inception()
        self.exists_with_prop(mapping)
        # self.print_wd()


class XkSq(Monument):

    def update_labels(self):
        """
        TODO
        Some of these contain several unprintable characters...
        0093 - 0096
        Maybe just go to the article and remove them?
        https://sq.wikipedia.org/wiki/Lista_e_Monumenteve_n%C3%AB_Kosov%C3%AB
        """
        print(self.name)
        return

    def set_no(self):
        self.add_statement("kosovo_monument_id", str(self.idno))

    def set_adm_location(self):
        """
        never wikilinked!
        E panjohur = unknown
        """
        print(municipality)

    def update_commonscat(self):
        """s
        the actual category names are not saved
        in the database, BUT
        a full category tree exists on commons,
        even though many of the cats are empty:
        https://commons.wikimedia.org/wiki/Category:Cultural_heritage_monuments_in_Kosovo_with_ID_No_3340
        These can be deduced from ID number
        """
        PATTERN = "Cultural heritage monuments in Kosovo with ID No "
        category = PATTERN + self.idno
        if commonscat_exists(category):
            self.add_statement("commonscat", category)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        self.exists("sq")
        self.update_commonscat()
        self.set_image("image")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_no()
        # self.set_location()
        # self.set_sagsnr()
        # self.set_address()
        # self.set_inception()
        self.exists_with_prop(mapping)
        # self.print_wd()


class ZaEn(Monument):

    def update_labels(self):
        name = remove_markup(self.site_name)
        self.add_label("en", name)

    def set_adm_location(self):
        # print(self.magisterial_district)
        return

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("sq")
        self.set_commonscat()
        self.set_image("image")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        # self.set_no()
        # self.set_location()
        self.exists_with_prop(mapping)
        # self.print_wd()


class RoRo(Monument):

    def update_labels(self):
        name = remove_markup(self.denumire)
        self.add_label("ro", name)

    def set_adm_location(self):
        return

    def set_no(self):
        self.add_statement("romanian_monument_id", self.cod)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("sq")
        self.set_commonscat()
        self.set_image("imagine")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_no()
        # self.set_location()
        self.exists_with_prop(mapping)
        # self.print_wd()


class CzCs(Monument):

    def update_labels(self):
        name = remove_markup(self.name)
        self.add_label("cs", name)

    def set_adm_location(self):
        """
        TODO
        Download all
        """
        print(self.municipality)

    def set_no(self):
        code = str(self.id_objektu)
        self.add_statement("czech_monument_id", code)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("sq")
        self.set_commonscat()
        self.set_image("image")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_no()
        # self.set_location()
        self.exists_with_prop(mapping)
        # self.print_wd()


class HuHu(Monument):

    def update_labels(self):
        name = remove_markup(self.name)
        self.add_label("hu", name)

    def set_adm_location(self):
        return

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("sq")
        self.set_commonscat()
        self.set_image("image")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        # self.set_no()
        # self.set_location()
        self.exists_with_prop(mapping)
        self.print_wd()


class PtPt(Monument):

    def update_labels(self):
        name = remove_markup(self.designacoes)
        self.add_label("pt", name)

    def update_descriptions(self):
        if self.has_non_empty_attribute("freguesia"):
            freg = remove_markup(self.freguesia)
            desc_en = "heritage site in " + freg + ", Portugal"
            self.add_description("en", desc_en)
            print(desc_en)

    def set_adm_location(self):
        if self.has_non_empty_attribute("freguesia"):
            parish = q_from_first_wikilink("pt", self.freguesia)
            self.add_statement("located_adm", parish)

    def set_no(self):
        code = self.id
        self.add_statement("igespar_id", str(code))

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("pt")
        self.update_descriptions()
        self.set_commonscat()
        self.set_image("imagem")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_no()
        # self.set_location()
        self.exists_with_prop(mapping)
        # self.print_wd()
