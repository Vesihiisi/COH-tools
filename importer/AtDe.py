from Monument import Monument
import importer_utils as utils
from os import path


MAPPING_DIR = "mappings"


class AtDe(Monument):

    def update_labels(self):
        de_label = self.name  # never wikilinked or wierd
        self.add_label("de", de_label)

    def set_street_address(self):
        """
        Set the street address.

        These look really nice, judging from a manual
        overview. The only quirk is stuff starting
        with bei -- "bei Marstallweg 20". Can it just
        be removed and the rest is a valid address,
        or does it indicate the whole address is imprecise
        and thus maybe shouldn't be included?
        """
        if self.has_non_empty_attribute("adresse"):
            address = self.adresse
            self.add_statement(
                "located_street", address)

    def set_heritage_id(self):
        heritage_id = self.objektid
        self.add_statement("austria_heritage_id", heritage_id)

    def set_monuments_all_id(self):
        """Map which column in table to ID in monuments_all."""
        self.monuments_all_id = self.objektid

    def set_adm_location(self):
        all_codes = self.data_files["municipalities"]
        if self.has_non_empty_attribute("gemeindekennzahl"):
            municip_code = str(self.gemeindekennzahl)
            match = [x["item"]
                     for x in all_codes if x["value"] == municip_code]
            self.add_statement("located_adm", municip_item=match[0])

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("de", "artikel")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.update_labels()
        self.set_country()
        self.set_image("foto")
        self.set_heritage()
        self.set_heritage_id()
        self.set_adm_location()
        self.set_street_address()
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
