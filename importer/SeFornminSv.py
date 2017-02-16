from Monument import Monument
import importer_utils as utils
from os import path


MAPPING_DIR = "mappings"


class SeFornminSv(Monument):

    def update_labels(self):
        """
        Some of the items have the 'namn' column
        filled out, and others don't.
        If it exists, it looks like:
            [[Grytahögen]]
             Kung Björns Grav
        In which case, use that as a label.
        Otherwise, use the RAÄ number as a label:
            Mellby 84:1
        """
        if len(self.namn) == 0:
            self.add_label("sv", self.raa_nr)
        else:
            self.add_label("sv", utils.remove_markup(self.namn))

    def set_descriptions(self):
        """
        All items should have the 'typ' field
        filled out:
            stensättning
        as well as a 'landskap':
            Blekinge
        These are used to construct a description
        in Swedish:
            stensättning i Blekinge
        If there's no specific 'typ',
        DESC_BASE is used as default.
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
        All items have a 'raa-nr'.
        """
        ref = self.wlm_source
        self.add_statement("raa-nr", self.raa_nr, refs=[ref])

    def set_adm_location(self):
        """
        Use offline mapping file
        to map municipality to P131.
        The column is 'kommun'.
        It looks like this:
            Alingsås
        Just the name of the municipality
        without the word kommun or genitive.
        """
        municip_dict = utils.load_json(path.join(
            MAPPING_DIR, "sweden_municipalities.json"))
        if self.kommun == "Göteborg":
            municip_name = "Gothenburg"
        else:
            municip_name = self.kommun
        pattern = municip_name.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "en"].lower() == pattern][0]
            ref = self.wlm_source
            self.add_statement("located_adm", municipality, refs=[ref])
        except IndexError:
            print("Could not parse municipality: {}.".format(self.kommun))
            return

    def set_type(self):
        """
        All items should have a 'typ', like:
            stensättning
        Use the lookup table from:
        https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/se-fornmin_(sv)/types
        If there's a match, use the more specific
        item as P31.
        Replace the original P31 rather than adding to it.
        """
        if self.has_non_empty_attribute("typ"):
            table = self.data_files["types"]["mappings"]
            type_to_search_for = self.typ.lower()
            try:
                special_type = [table[x]["items"]
                                for x in table
                                if x.lower() == type_to_search_for][0][0]
                self.substitute_statement("is", special_type)
            except IndexError:
                return

    def get_socken(self, socken_name, landskap_name):
        """
        Each item has both a 'landskap' and a 'socken'.
        Combine them and get corresponding WD item
        via swedish wikipedia.
        """
        return utils.socken_to_q(socken_name, landskap_name)

    def set_location(self):
        """
        If there's a 'plats' and it's wikilinked use it as location:
            [[Tyresta]]
        It's just a handful of items that have it, though.
        But all should have socken/landskap,
        so use that as location as well.
        """
        if self.has_non_empty_attribute("plats"):
            if "[[" in self.plats:
                wikilinks = utils.get_wikilinks(self.plats)
                if len(wikilinks) == 1:
                    target_page = wikilinks[0].title
                    wd_item = utils.q_from_wikipedia("sv", target_page)
                    ref = self.wlm_source
                    self.add_statement("location", wd_item, refs=[ref])
        if self.has_non_empty_attribute("socken"):
            ref = self.wlm_source
            self.add_statement("location", self.get_socken(
                self.socken, self.landskap), refs=[ref])

    def set_inception(self):
        """
        TODO?
        This is messy and not super prioritized...
        Only a handful of items have it,
        and it looks mostly like
            folkvandringstid ca 400 - 550 e Kr
            sentida
        """
        return

    def set_monuments_all_id(self):
        """
        Map which column name in specific table
        is used as ID in monuments_all.
        """
        self.monuments_all_id = self.id

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_is()
        self.set_heritage()
        self.set_source()
        self.set_registrant_url()
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
