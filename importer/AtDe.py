from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


MAPPING_DIR = "mappings"


class AtDe(Monument):

    def get_type_keyword(self):
        """
        Extract type of monument from name.

        Does matching of name against list of monument
        types from
        https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/at_(de)/types
        """
        raw_name = self.name.lower()
        types = self.data_files["types"]["mappings"]
        keywords = list(types.keys())
        keywords = [x.lower() for x in keywords]
        return utils.get_longest_match(raw_name, keywords)

    def set_type(self):
        """
        Set specific P31, if possible.

        Default P31 is cultural property.
        If extracting a type keyword succeeded,
        use the more specific item as P31.
        """
        types = self.data_files["types"]["mappings"]
        type_match = self.get_type_keyword()
        if type_match:
            if isinstance(type_match, list):
                # multiple matches - report
                self.add_to_report("type", self.name, "is")
            else:
                # single match - add
                match_item = [types[x]["items"]
                              for x in types if x.lower() == type_match][0][0]
                self.substitute_statement("is", match_item)
        else:
            # no matches - report
            self.add_to_report("type", self.name, "is")

    def update_labels(self):
        """
        Set the labels.

        The data does not contain any markup,
        so we're adding them as is.
        """
        self.add_label("de", self.name)

    def set_descriptions(self):
        """
        Set descriptions in German.

        Base format: $type in $country
        If specific type in German exists, substitute for $type.
        If municipality name exists, insert it
        """
        type_match = self.get_type_keyword()
        municipality_name = self.get_municipality_name()
        base_desc_german = "{} in {}"
        place_german = "Österreich"
        type_german = "Denkmalgeschütztes Objekt"

        if isinstance(type_match, str):
            type_german = type_match.title()
        if municipality_name:
            place_german = municipality_name
        desc_german = base_desc_german.format(
            type_german, place_german)

        self.add_description("de", desc_german)

    def set_street_address(self):
        """
        Set the street address.

        Most of these look good. Patterns for invalid ones:
        * 251, gegenüber
          Filtering by "starts with digit" and "contains comma",
          as we can't rely only on "starts with digit" because
          10. Oktober-Straße 18 is legit.
        * zwischen Entensteinstraße 36 u. 38
          Filtering by "zwischen".
        * 76
          Filtering by containing only digits.
        """
        bad_address = None
        if self.has_non_empty_attribute("adresse"):
            if (utils.first_char_is_number(self.adresse) and
                    "," in self.adresse):
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
        """Set the heritage ID, P2951."""
        self.add_statement("austria_heritage_id", self.objektid)

    def set_monuments_all_id(self):
        """Map which column in table to ID in monuments_all."""
        self.monuments_all_id = self.objektid

    def get_municipality_name(self):
        """Get municipality name based on gemeindekennzahl."""
        all_codes = self.data_files["municipalities"]
        municip_code = str(self.gemeindekennzahl)
        match = [x["itemLabel"]
                 for x in all_codes if x["value"] == municip_code]
        if len(match) == 1:
            return match[0]

    def set_adm_location(self):
        """
        Set the administrative location (municipality).

        Using the gemeindekennzahl field, municipality ID,
        mapped to municipality WD items in external file.
        """
        all_codes = self.data_files["municipalities"]
        if self.has_non_empty_attribute("gemeindekennzahl"):
            municip_code = str(self.gemeindekennzahl)
            match = [x["item"]
                     for x in all_codes if x["value"] == municip_code]
            if len(match) == 1:
                self.add_statement("located_adm", match[0])
            else:
                self.add_to_report(
                    "gemeindekennzahl", municip_code, "located_adm")

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("de", "artikel")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.update_labels()
        self.set_descriptions()
        self.set_is()
        self.set_type()
        self.set_country()
        self.set_image("foto")
        self.set_heritage()
        self.set_heritage_id()
        self.set_adm_location()
        self.set_street_address()
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("at", "de", AtDe)
    dataset.data_files = {"municipalities": "austria_municipalities.json"}
    dataset.lookup_downloads = {"types": "at_(de)/types"}
    importer.main(args, dataset)
