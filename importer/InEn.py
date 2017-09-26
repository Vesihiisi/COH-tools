from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class InEn(Monument):

    def set_adm_location(self):
        """
        Set the Admin Location.

        Try using District first, from linked article or match
        the unlinked text via an external list.

        If that doesn't work, try the higher state level.
        This one is matched via ISO code.
        """
        adm_q = None

        if utils.count_wikilinks(self.district) == 1:
            adm_q = utils.q_from_first_wikilink("en", self.district)
        else:
            d = self.district
            district_dic = self.data_files["districts"]
            adm_match = utils.get_item_from_dict_by_key(dict_name=district_dic,
                                                        search_term=d,
                                                        search_in="itemLabel")
            if len(adm_match) == 1:
                adm_q = adm_match[0]

        if adm_q is None:  # try state instead, which is larger
            iso = self.state_iso
            state_dic = self.data_files["states"]
            state_match = utils.get_item_from_dict_by_key(dict_name=state_dic,
                                                          search_term=iso,
                                                          search_in="iso")
            if len(state_match) == 1:
                adm_q = state_match[0]

        if adm_q:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report("district", self.district, "located_adm")

    def set_location(self):
        """
        Set the Location.

        The Address field is not good for addresses, but often
        consists of a linked location.
        Otherwise, use a linked Location field.
        """
        loc_q = None

        if self.has_non_empty_attribute("address"):
            if utils.count_wikilinks(self.address) == 1:
                loc_q = utils.q_from_first_wikilink("en", self.address)

        if loc_q is None and self.has_non_empty_attribute("location"):
            if utils.count_wikilinks(self.location) == 1:
                loc_q = utils.q_from_first_wikilink("en", self.location)

        if loc_q:
            self.add_statement("location", loc_q)
        else:
            self.add_to_report("address", self.address, "location")

    def set_heritage(self):
        """Set correct heritage status."""
        ranks = {
            "N": "Q17047615",  # Monument of National Importance
            "S": "Q17047640"  # State Protected Monument
        }
        marker = self.number[0]
        self.add_statement("heritage_status", ranks[marker])

    def update_labels(self):
        english = None
        if self.has_non_empty_attribute("monument_article"):
            english = self.monument_article
        else:
            if self.has_non_empty_attribute("description"):
                english = utils.remove_markup(self.description)

        if english is not None:
            self.add_label("en", english)

    def update_descriptions(self):
        ranks = {
            "N": "Monument of National Importance",
            "S": "State Protected Monument"
        }
        mon_type = ranks[self.number[0]]
        english = "{} in India".format(mon_type)
        self.add_description("en", english)

    def set_heritage_id(self):
        self.add_statement("asi", self.number)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("number")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_heritage()
        self.set_country()
        self.set_location()
        self.set_is()
        self.set_commonscat()
        self.set_coords()
        self.set_image()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("in", "en", InEn)
    dataset.data_files = {
        "districts": "india_districts.json",
        "states": "india_states.json"}
    importer.main(args, dataset)
