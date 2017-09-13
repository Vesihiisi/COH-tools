from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class PhEn(Monument):

    def update_labels(self):
        english = utils.remove_markup(self.site_name)
        self.add_label("en", english)

    def update_descriptions(self):
        english = "Declared Cultural Property in the Philippines"
        self.add_description("en", english)

    def set_location(self):
        loc_q = None
        if self.has_non_empty_attribute("location"):
            if utils.count_wikilinks(self.location) == 1:
                loc_q = utils.q_from_first_wikilink("en", self.location)

            if loc_q:
                self.add_statement("location", loc_q)
            else:
                self.add_to_report("location", self.location, "location")

    def set_adm_location(self):
        """
        Set the administrative location.

        First, try getting it via the wikilinked 'province'
        and check that it's present in the province mapping.
        If that fails, get the larger region via 'region-iso'
        and mapping.
        """
        adm_q = None
        prov_dic = self.data_files["provinces"]
        reg_dic = self.data_files["regions"]

        if utils.count_wikilinks(self.province) == 1:
            adm_q_try = utils.q_from_first_wikilink("en", self.province)
            if adm_q_try in [x["item"] for x in prov_dic]:
                adm_q = adm_q_try

        if adm_q is None:
            iso = self.region_iso
            iso_match = utils.get_item_from_dict_by_key(reg_dic,
                                                        search_term=iso,
                                                        search_in="iso")
            if len(iso_match) == 1:
                adm_q = iso_match[0]

        if adm_q:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report("province", self.province, "located_adm")

    def set_wd_item_from_name(self):
        """
        Set the WD item as the item linked from 'name'.

        The reason is that there's no monument_article
        in this table.
        """
        if utils.count_wikilinks(self.site_name) == 1:
            linked_q = utils.q_from_first_wikilink("en", self.site_name)
            self.set_wd_item(linked_q)

    def set_heritage_id(self):
        """Set the WLM ID property."""
        self.add_statement("wlm_id", self.cp_wmph_id)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("cp_wmph_id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_adm_location()
        self.set_location()
        self.set_heritage()
        self.set_heritage_id()
        self.set_coords()
        self.set_commonscat()
        self.set_image()
        self.update_labels()
        self.update_descriptions()
        self.set_is()
        self.set_wd_item_from_name()  # there's no monument_article
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("ph", "en", PhEn)
    dataset.data_files = {"regions": "philippines_regions.json",
                          "provinces": "philippines_provinces.json"}
    importer.main(args, dataset)
