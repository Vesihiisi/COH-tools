from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class BeBruNl(Monument):

    def set_special_is(self):
        objtype = self.objtype.lower()
        types = self.data_files["type"]["mappings"]
        special_types = [types[x]["items"]
                         for x in types if x.lower() == objtype]
        if len(special_types) > 0:
            self.remove_statement("is")
            for q in special_types:
                self.add_statement("is", q)

    def set_architect(self):
        if self.has_non_empty_attribute("bouwdoor"):
            if utils.count_wikilinks(self.bouwdoor) == 1:
                arch_q = utils.q_from_first_wikilink("nl", self.bouwdoor)
                self.add_statement("architect", arch_q)

    def update_labels(self):
        dutch = utils.remove_markup(self.omschrijving)
        self.add_label("nl", dutch)

    def set_building_year(self):
        if self.has_non_empty_attribute("bouwjaar"):
            if utils.legit_year(self.bouwjaar):
                self.add_statement(
                    "inception", {"time_value": {"year": self.bouwjaar}})

    def set_monuments_all_id(self):
        self.monuments_all_id = self.code

    def set_heritage_id(self):
        self.add_statement("heritage_brussels", self.code)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("nl", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_source()
        self.set_registrant_url()
        self.set_heritage_id()
        self.set_heritage()
        self.set_country()
        self.set_image()
        self.set_commonscat()
        self.set_architect()
        self.set_is()
        self.set_special_is()
        self.set_coords(("lat", "lon"))
        self.set_building_year()
        self.update_labels()
        # self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("be-bru", "nl", BeBruNl)
    dataset.data_files = {}
    dataset.lookup_downloads = {"type": "be-bru (nl)/objtype"}
    importer.main(args, dataset)
