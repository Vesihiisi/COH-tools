from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class RoRo(Monument):

    def set_adm_location(self):
        counties = self.data_files["counties"]
        adm_code = self.judetul_iso
        county_item = utils.get_item_from_dict_by_key(dict_name=counties,
                                                      search_term=adm_code,
                                                      search_in="iso_code")
        if len(county_item) == 1:
            self.add_statement("located_adm", county_item[0])
        else:
            self.add_to_report("judetul_iso",
                               self.judetul_iso,
                               "located_adm")

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.cod)

    def set_wlm_id(self):
        """
        Set the WLM ID.

        Do _not_ use the Romania LMI code (P1770)
        as it's made up and has no relevance to the
        real world.
        """
        ccode = self.mapping["country_code"].upper()
        wlm_id = "{}-{}".format(ccode, self.cod)
        self.add_statement("wlm_id", wlm_id)

    def update_descriptions(self):
        adm_code = self.judetul_iso
        counties = self.data_files["counties"]
        county_item = [x for x in counties if x["iso_code"] == adm_code]
        if len(county_item) == 1:
            place_name = "{}, Romania".format(county_item[0]["itemLabel"])
        else:
            place_name = "Romania"
        desc = "heritage site in {}".format(place_name)
        self.add_description("en", desc)

    def update_labels(self):
        romanian = utils.remove_markup(self.denumire)
        self.add_label("ro", romanian)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage()
        self.set_wlm_id()
        self.set_country()
        self.set_adm_location()
        self.set_coords()
        self.set_commonscat()
        self.set_image("imagine")
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("ro", "ro", RoRo)
    dataset.data_files = {"counties": "romania_counties.json"}
    importer.main(args, dataset)
