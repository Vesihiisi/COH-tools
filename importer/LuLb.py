import dateparser
from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class LuLb(Monument):

    def set_location(self):
        """
        Set the Location.

        Use a linked place name, and check it's different
        from the Administrative Location, to avoid duplicates.
        """
        if self.has_non_empty_attribute("uertschaft"):
            loc_q = utils.q_from_wikipedia("lb", self.uertschaft)
            if loc_q:
                try:
                    adm_loc = self.wd_item["statements"]["P131"][0]["value"]
                except KeyError:
                    adm_loc = None
                if loc_q != adm_loc:
                    self.add_statement("location", loc_q)
            else:
                self.add_to_report("uertschaft", self.uertschaft, "location")

    def set_adm_location(self):
        """Set the Administrative Location via Region iso code."""
        adm_q = None
        dis_dic = self.data_files["districts"]

        if self.has_non_empty_attribute("region_iso"):
            iso = self.region_iso
            dis_match = utils.get_item_from_dict_by_key(
                dict_name=dis_dic, search_in="iso", search_term=iso)
            if len(dis_match) == 1:
                adm_q = dis_match[0]
        if adm_q:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report("region-iso", self.region_iso, "located_adm")

    def set_heritage_id(self):
        """Set WLM ID with country's ISO-prefix."""
        ccode = self.mapping["country_code"].upper()
        id_no = "{}-{}".format(ccode, self.id)
        self.add_statement("wlm_id", id_no)

    def update_descriptions(self):
        descs = {"en": "National Monument of Luxembourg"}
        for lg in descs:
            self.add_description(lg, descs[lg])

    def update_labels(self):
        lb = utils.remove_markup(self.offiziellen_numm)
        self.add_label("lb", lb)

    def set_heritage(self):
        """
        Set the heritage status.

        If possible, add start date from Klasseiert Zenter
        as quantifier, otherwise fall back on the default.
        """
        if self.has_non_empty_attribute("klasseiert_zenter"):
            heritage = self.mapping["heritage"]["item"]
            start_raw = self.klasseiert_zenter
            date_parsed = dateparser.parse(start_raw)
            if date_parsed:
                date_dict = utils.datetime_object_to_dict(date_parsed)
                qualifier = {"start_time": {"time_value": date_dict}}
                self.add_statement("heritage_status",
                                   heritage, quals=qualifier)
            else:
                super().set_heritage()
        else:
            super().set_heritage()

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("lb", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage()
        self.set_heritage_id()
        self.set_country()
        self.set_coords()
        self.set_adm_location()
        self.set_location()
        self.set_is()
        self.set_image("bild")
        self.set_commonscat()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("lu", "lb", LuLb)
    dataset.data_files = {"districts": "luxembourg_districts.json"}
    importer.main(args, dataset)
