from Monument import Monument, Dataset
import dateparser
import importer_utils as utils
import importer as importer


class UyEs(Monument):

    def set_inception(self):
        """Set building year if parseable."""
        if self.has_non_empty_attribute("construido"):
            date_dict = None
            if utils.legit_year(self.construido):
                # plain years cannot be sent to dateparser
                date_dict = {"year": self.construido}
            else:
                date_p = dateparser.parse(self.construido)
                if date_p:
                    date_dict = utils.datetime_object_to_dict(date_p)

            if date_dict:
                self.add_statement("inception", utils.package_time(date_dict))
            else:
                self.add_to_report("construido", self.construido, "inception")

    def set_location(self):
        """
        Set the Location.

        Use the linked Localidad if available,
        and if it's not linked, try and see if there's
        an article anyway. Compare against external
        list of settlements.
        """
        loc_dic = self.data_files["settlements"]
        loc_q = None

        if self.has_non_empty_attribute("localidad"):
            loc_raw = self.localidad
            if utils.count_wikilinks(loc_raw) == 1:
                loc_try = utils.q_from_first_wikilink("es", loc_raw)
                loc_match = utils.get_item_from_dict_by_key(
                    dict_name=loc_dic,
                    search_term=loc_try,
                    search_in="item")
                if len(loc_match) == 1:
                    loc_q = loc_try
            else:
                loc_try = utils.q_from_wikipedia("es", loc_raw)
                loc_match = utils.get_item_from_dict_by_key(
                    dict_name=loc_dic,
                    search_term=loc_try,
                    search_in="item")
                if len(loc_match) == 1:
                    loc_q = loc_try

            if loc_q:
                self.add_statement("location", loc_q)
            else:
                self.add_to_report("localidad", self.localidad, "location")

    def set_adm_location(self):
        """Set the Admin Location using department ISO code."""
        self.set_from_dict_match(
            lookup_dict=self.data_files["departments"],
            dict_label="iso",
            value_label="dep_iso",
            prop="located_adm"
        )

    def set_directions(self):
        if self.has_non_empty_attribute("direccion"):
            monolingual = utils.package_monolingual(
                utils.remove_markup(self.direccion), 'es')
            self.add_statement("directions", monolingual)

    def set_wd_item_via_name(self):
        """
        Attempt to set wd item via name.

        Populates self.monument_article, the value then gets used in
        find_matching_wikidata() with extra precautionary logic.
        """
        if utils.count_wikilinks(self.monumento) == 1:
            self.monument_article = utils.get_wikilinks(
                self.monumento)[0].title

    def update_labels(self):
        es_name = utils.remove_markup(self.monumento)
        self.add_label("es", es_name)

    def update_descriptions(self):
        en = "cultural heritage monument of Uruguay"
        self.add_description("en", en)

    def set_heritage_id(self):
        wlm_code = self.mapping["table_name"].upper()
        self.add_statement("wlm_id", "{}-{}".format(wlm_code, self.id))
        self.add_disambiguator(str(self.id))

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_adm_location()
        self.set_directions()
        self.set_location()
        self.set_is()
        self.set_inception()
        self.set_heritage()
        self.set_coords()
        self.set_image()
        self.set_heritage_id()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item_via_name()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("uy", "es", UyEs)
    dataset.data_files = {
        "departments": "uruguay_departments.json",
        "settlements": "uruguay_settlements.json"
    }
    importer.main(args, dataset)
