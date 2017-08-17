from Monument import Monument
import importer_utils as utils


class KeEn(Monument):

    def update_descriptions(self):
        descs = {"en": "National Monument of Kenya"}
        for lang in descs:
            self.add_description(lang, descs[lang])

    def update_labels(self):
        english = utils.remove_markup(self.name)
        self.add_label("en", english)

    def set_heritage_id(self):
        self.add_statement("wlm_id", str(self.id))

    def set_monuments_all_id(self):
        self.monuments_all_id = str(self.id)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("en", "monument_article")

    def set_heritage_start(self):
        if self.has_non_empty_attribute("gazette"):
            heritage = self.mapping["heritage"]["item"]
            date_dict = utils.date_to_dict(self.gazette, "%Y")
            qualifier = {"start_time": {"time_value": date_dict}}
            self.substitute_statement("heritage_status", heritage, qualifier)

    def set_adm_location(self):
        location_match = None
        if self.has_non_empty_attribute("location"):
            location_match = utils.q_from_first_wikilink("en", self.location)
        if not location_match and self.has_non_empty_attribute("county"):
            location_match = utils.q_from_first_wikilink("en", self.county)
        if location_match:
            self.add_statement("located_adm", location_match)
        else:
            self.add_to_report("county", self.county, "located_adm")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_commonscat()
        self.set_is()
        self.set_heritage_id()
        self.set_heritage()
        self.set_heritage_start()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))
