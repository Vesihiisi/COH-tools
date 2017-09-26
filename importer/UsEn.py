import dateparser
from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class UsEn(Monument):

    def set_location(self):
        """Set Location based on linked article."""
        if self.has_non_empty_attribute("city"):
            if utils.count_wikilinks(self.city) == 1:
                loc_q = utils.q_from_first_wikilink("en", self.city)
                self.add_statement("location", loc_q)
            else:
                self.add_to_report("city", self.city, "location")

    def set_adm_location(self):
        """
        Set administrative location.

        First, try using linked County matched against
        external list.
        If that doesn't yield, use ISO code of State
        against external list.
        """
        adm_q = None
        county_dic = self.data_files["counties"]
        state_dic = self.data_files["states"]

        if utils.count_wikilinks(self.county) == 1:
            county_q = utils.q_from_first_wikilink("en", self.county)
            if county_q in [x["item"] for x in county_dic]:
                adm_q = county_q

        if adm_q is None:
            s_iso = self.state_iso.upper()
            state_match = utils.get_item_from_dict_by_key(dict_name=state_dic,
                                                          search_term=s_iso,
                                                          search_in="iso")
            if len(state_match) == 1:
                adm_q = state_match[0]

        if adm_q:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report("county", self.county, "located_adm")

    def set_heritage(self):
        """
        Set heritage status.

        Based on
        https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/us_(en)/type
        If possible, add date of protection as quantifier.
        """

        qualifier = None

        if self.has_non_empty_attribute("date"):
            d_parsed = dateparser.parse(self.date)
            if d_parsed:
                date_dict = utils.datetime_object_to_dict(d_parsed)
                qualifier = {"start_time": {"time_value": date_dict}}

        her_raw = self.type.lower()

        her_dic = self.data_files["her_types"]["mappings"]
        her_match = utils.get_matching_items_from_dict(her_raw, her_dic)
        if len(her_match) == 1:
            her_q = her_match[0]

        self.add_statement("heritage_status", her_q, quals=qualifier)

    def update_labels(self):
        self.add_label("en", utils.remove_markup(self.name))

    def set_heritage_id(self):
        self.add_statement("nhrp", str(self.refnum))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("en", "article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("refnum")
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_adm_location()
        self.set_is()
        self.set_heritage()
        self.set_heritage_id()
        self.set_image()
        self.set_commonscat()
        self.set_coords()
        self.update_labels()
        self.set_location()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("us", "en", UsEn)
    dataset.data_files = {
        "counties": "us_counties.json",
        "states": "us_states.json"}
    dataset.lookup_downloads = {"her_types": "us_(en)/type"}
    importer.main(args, dataset)
