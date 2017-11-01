from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class KeEn(Monument):

    def update_descriptions(self):
        descs = {"en": "National Monument of Kenya"}
        for lang in descs:
            self.add_description(lang, descs[lang])

    def update_labels(self):
        english = utils.remove_markup(self.name)
        self.add_label("en", english)

    def set_heritage_id(self):
        prefix = self.mapping["table_name"].upper()
        wlm_id = "{}-{}".format(prefix, str(self.id))
        self.add_statement("wlm_id", wlm_id)

    def set_heritage_start(self):
        if self.has_non_empty_attribute("gazette"):
            heritage = self.mapping["heritage"]["item"]
            date_dict = utils.date_to_dict(self.gazette, "%Y")
            qualifier = {"start_time": {"time_value": date_dict}}
            self.substitute_statement("heritage_status", heritage, qualifier)

    def set_adm_location(self):
        adm_match = None
        if self.has_non_empty_attribute("county"):
            adm_match = utils.q_from_first_wikilink("en", self.county)

        if adm_match:
            self.add_statement("located_adm", adm_match)
        else:
            self.add_to_report("county", self.county, "located_adm")

    def set_location(self):
        loc_match = None
        if self.has_non_empty_attribute("location"):
            loc_match = utils.q_from_first_wikilink("en", self.location)

        if loc_match:
            self.add_statement("location", loc_match)
        else:
            self.add_to_report("location", self.location, "location")

    def set_directions(self):
        if self.has_non_empty_attribute("address"):
            dirs = utils.package_monolingual(self.address, "en")
            self.add_statement("directions", dirs)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_location()
        self.set_commonscat()
        self.set_is()
        self.set_heritage_id()
        self.set_heritage()
        self.set_heritage_start()
        self.set_directions()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("ke", "en", KeEn)
    importer.main(args, dataset)
