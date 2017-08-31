from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class NlAwNl(Monument):

    def set_address(self):
        if self.has_non_empty_attribute("adres"):
            if utils.contains_digit(self.adres):
                town = utils.remove_markup(self.plaats)
                address = "{}, {}".format(self.adres, town)
                self.add_statement("located_street", address)
            else:
                self.add_to_report("adres", self.adres, "located_street")

    def update_labels(self):
        nl = utils.remove_markup(self.omschrijving)
        self.add_label("nl", nl)

    def set_adm_location(self):
        aruba = "Q21203"
        self.add_statement("located_adm", aruba)

    def set_location(self):
        loc_q = None
        loc_dic = self.data_files["settlements"]
        if self.has_non_empty_attribute("plaats"):
            if utils.count_wikilinks(self.plaats) == 1:
                loc_q = utils.q_from_first_wikilink("nl", self.plaats)
            else:
                loc_match = [x for x in loc_dic if x[
                    "itemLabel"] == self.plaats]
                if len(loc_match) == 1:
                    loc_q = loc_match[0]["item"]
        if loc_q:
            self.add_statement("location", loc_q)
        else:
            self.add_to_report("plaats", self.plaats, "location")

    def set_inception(self):
        if self.has_non_empty_attribute("bouwjaar"):
            if utils.legit_year(self.bouwjaar):
                inc_year = {"time_value": {"year": self.bouwjaar}}
                self.add_statement("inception", inc_year)
            else:
                self.add_to_report("bouwjaar", self.bouwjaar, "inception")

    def set_heritage_id(self):
        country = self.mapping["country_code"].upper()
        wlm = "{}-{}".format(country, str(self.objectnr))
        self.add_statement("wlm_id", wlm)

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = self.objectnr

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("nl", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_heritage_id()
        self.set_heritage()
        self.set_country()
        self.set_location()
        self.set_adm_location()
        self.set_address()
        self.set_is()
        self.set_coords(("lat", "lon"))
        self.set_image()
        self.set_commonscat()
        self.set_inception()
        self.update_labels()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("nl-aw", "nl", NlAwNl)
    dataset.data_files = {"settlements": "aruba_settlements.json"}
    dataset.lookup_downloads = {}
    importer.main(args, dataset)
