from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class UaUk(Monument):

    def set_adm_location(self):
        """
        Set administrative location.

        'municipality' contains both wlinked
        and clean values.
        """
        adm_match = None
        adm_dict = self.data_files["administrative"]
        obl_dict = self.data_files["oblasti"]

        if self.has_non_empty_attribute("municipality"):
            if len(utils.get_wikilinks(self.municipality)) == 1:
                adm_match = utils.q_from_first_wikilink("uk",
                                                        self.municipality)

        if not adm_match:
            adm_try = utils.get_item_from_dict_by_key(dict_name=adm_dict,
                                                      search_term=self.municipality,
                                                      search_in="itemLabel")
            if len(adm_try) == 1:
                adm_match = adm_try[0]

        if not adm_match:
            iso = self.iso_oblast
            adm_try = utils.get_item_from_dict_by_key(dict_name=obl_dict,
                                                      search_in="iso",
                                                      search_term=iso)
            if len(adm_try) == 1:
                adm_match == adm_try[0]

        self.add_statement("located_adm", adm_match)

    def set_heritage_id(self):
        wlm = "{}-{}".format(self.mapping["table_name"].upper(), self.id)
        self.add_statement("wlm_id", wlm)
        # self.add_disambiguator(str(self.id))

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_coords()
        self.set_is()
        self.set_country()
        self.set_adm_location()
        self.set_heritage()
        self.set_heritage_id()
        self.set_image()
        self.set_commonscat()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("ua", "uk", UaUk)
    dataset.data_files = {
        "oblasti": "ukraine_oblasti.json",
        "administrative": "ukraine_admin.json"  # http://tinyurl.com/y7rzg6wt
    }
    importer.main(args, dataset)
