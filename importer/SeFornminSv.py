from Monument import Monument
import importer_utils as utils
from os import path


MAPPING_DIR = "mappings"


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
        return utils.socken_to_q(socken_name, landskap_name)

    def set_location(self):
        if self.has_non_empty_attribute("plats"):
            if "[[" in self.plats:
                wikilinks = utils.get_wikilinks(self.plats)
                if len(wikilinks) == 1:
                    target_page = wikilinks[0].title
                    wd_item = utils.q_from_wikipedia("sv", target_page)
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
