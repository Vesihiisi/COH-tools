import dateparser
from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class TnFr(Monument):

    def set_street_address(self):
        """
        Set the street address.

        Works if the source data contains a digit.
        Since the place is not included, transpose
        it from the place name.
        """
        if self.has_non_empty_attribute("adresse"):
            addr_raw = utils.remove_markup(self.adresse)
            if utils.contains_digit(addr_raw):
                settlement = utils.remove_markup(self.site)
                address = "{}, {}".format(addr_raw, settlement)
                self.add_statement("located_street", address)
            else:
                monolingual = utils.package_monolingual(addr_raw, 'fr')
                self.add_statement("directions", monolingual)

    def set_location(self):
        """
        Set the location.

        If present, use the wikilink, otherwise
        match value against list of settlements.
        """
        loc_q = None
        loc_raw = self.site
        if utils.count_wikilinks(loc_raw) == 1:
            loc_q = utils.q_from_first_wikilink("fr", loc_raw)
        else:
            loc_dic = self.data_files["settlements"]
            loc_match = utils.get_item_from_dict_by_key(dict_name=loc_dic,
                                                        search_term=loc_raw,
                                                        search_in="itemLabel")
            if len(loc_match) == 1:
                loc_q = loc_match[0]

        if loc_q:
            self.add_statement("location", loc_q)
        else:
            self.add_to_report("site", self.site, "location")

    def set_admin_location(self):
        """
        Set the admin location.

        Use the iso code of the gouvernorat for exact
        matching against list.
        """
        adm_q = None
        iso = self.gouvernorat_iso
        admin_dic = self.data_files["admin"]
        admin_match = utils.get_item_from_dict_by_key(dict_name=admin_dic,
                                                      search_term=iso,
                                                      search_in="iso")
        if len(admin_match) == 1:
            adm_q = admin_match[0]
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report("gouvernorat_iso",
                               self.gouvernorat_iso, "located_adm")

    def set_heritage(self):
        """
        Set heritage status with optional qualifiers.

        Use 'decret' as 'described at url'.
        Extract date from 'date' as 'start time'.
        """
        quals = {}
        heritage_item = self.mapping["heritage"]["item"]

        urls = utils.get_external_links(self.decret)
        if len(urls) == 1:
            quals["described_at_url"] = urls[0].strip_code()
        elif len(urls) > 1:
            self.add_to_report("decret", self.decret, "described_at_url")

        date_templates = utils.wparser.parse(self.date).filter_templates()
        if (len(date_templates) == 1 and
                date_templates[0].name.lower() == 'date'):
            templ = date_templates[0].params
            date_words = "{} {} {}".format(templ[0], templ[1], templ[2])
            date_parsed = dateparser.parse(date_words, languages=['fr'])
            if date_parsed:
                date_dict = utils.datetime_object_to_dict(date_parsed)
                quals["start_time"] = {"time_value": date_dict}
        elif len(date_templates) > 0:
            self.add_to_report("date", self.date, "start_time")

        self.add_statement("heritage_status", heritage_item, quals)

    def update_labels(self):
        french = utils.remove_markup(self.monument)
        self.add_label("fr", french)

    def set_heritage_id(self):
        wlm_code = self.mapping["table_name"].upper()
        wlm_id = "{}-{}".format(wlm_code, str(self.id))
        self.add_statement("wlm_id", wlm_id)

        self.add_disambiguator(str(self.id), 'fr')

    def update_descriptions(self):
        english = "listed monument of Tunisia"
        self.add_description("en", english)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_commonscat()
        self.set_image()
        self.set_coords()
        self.set_country()
        self.set_heritage()
        self.set_heritage_id()
        self.set_admin_location()
        self.set_location()
        self.set_street_address()
        self.set_is()
        self.update_descriptions()
        self.update_labels()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("tn", "fr", TnFr)
    dataset.data_files = {"admin": "tunisia_admin.json",
                          "settlements": "tunisia_settlements.json"}
    importer.main(args, dataset)
