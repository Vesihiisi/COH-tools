from Monument import Monument
import importer_utils as utils


MAPPING_DIR = "mappings"


class AtDe(Monument):

    def update_labels(self):
        de_label = self.name  # never wikilinked or wierd
        self.add_label("de", de_label)

    def set_street_address(self):
        """
        Set the street address.

        Most of these look good. Patterns for invalid ones:
        * 251, gegenüber
          Filtering by "starts with digit" and "contains comma",
          as we can't rely only on "starts with digit" because
          10. Oktober-Straße 18 is legit.
        * zwischen Entensteinstraße 36 u. 38
          Filtering by "zwischen", between.
        * 76
          Filtering by containing only digits.
        """
        bad_address = None
        if self.has_non_empty_attribute("adresse"):
            if utils.first_char_is_number(self.adresse) and "," in self.adresse:
                bad_address = self.adresse
            elif "zwischen" in self.adresse:
                bad_address = self.adresse
            elif self.adresse.isdigit():
                bad_address = self.adresse
            else:
                address = self.adresse
                self.add_statement(
                    "located_street", address)
        if bad_address:
            self.add_to_report("adresse", self.adresse, "located_street")

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
