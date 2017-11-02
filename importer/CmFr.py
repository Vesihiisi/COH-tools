from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class CmFr(Monument):

    def update_descriptions(self):
        english = "monument of Cameroon"
        self.add_description("en", english)

    def update_labels(self):
        french = utils.remove_markup(self.nom)
        self.add_label("fr", french)

    def set_location(self):
        """Set location, using wikilinked value."""
        if self.has_non_empty_attribute("ville"):
            if utils.count_wikilinks(self.ville) == 1:
                loc_q = utils.q_from_first_wikilink("fr", self.ville)
                self.add_statement("location", loc_q)
            else:
                self.add_to_report("ville", self.ville, "location")

    def set_adm_location(self):
        """Set Adm Location, using the iso of the region."""
        reg_dic = self.data_files["regions"]
        iso = self.region_iso
        adm_match = utils.get_item_from_dict_by_key(dict_name=reg_dic,
                                                    search_term=iso,
                                                    search_in="iso")
        if len(adm_match) == 1:
            self.add_statement("located_adm", adm_match[0])
        else:
            self.add_to_report("region_iso", self.region_iso, "located_adm")

    def set_heritage_id(self):
        wml_code = self.mapping["table_name"].upper()
        self.add_statement("wlm_id", "{}-{}".format(wml_code, str(self.id)))

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_country()
        self.set_adm_location()
        self.set_location()
        self.set_heritage()
        self.set_commonscat()
        self.set_image()
        self.set_coords()
        self.set_is()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("cm", "fr", CmFr)
    dataset.data_files = {"regions": "cameroon_regions.json"}
    importer.main(args, dataset)
