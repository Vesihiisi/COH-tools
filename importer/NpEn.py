from Monument import Monument
import importer_utils as utils


class NpEn(Monument):

    def update_descriptions(self):
        descs = {"en": "cultural property in {}"}
        countries = {"en": "Nepal"}
        for lang in descs:
            if self.has_non_empty_attribute("district"):
                location = "{}, {}".format(self.district, countries[lang])
            else:
                location = countries[lang]
            description = descs[lang].format(location)
            self.add_description(lang, description)

    def update_labels(self):
        self.add_label("en", utils.remove_markup(self.description))

    def set_adm_location(self):
        match = None
        districts = self.data_files["districts"]
        zones = self.data_files["zones"]
        distr_match = [x for x in districts if self.district in x["itemLabel"]]
        if len(distr_match) == 1:
            match = distr_match[0]["item"]
        else:
            zone_match = [x for x in zones if x["iso"] == self.zone_iso]
            if len(zone_match) == 1:
                match = zone_match[0]["item"]
        if match:
            self.add_statement("located_adm", match)
        else:
            self.add_to_report("district", self.district, "located_adm")

    def set_monuments_all_id(self):
        self.monuments_all_id = str(self.number)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("de", "artikel")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_is()
        self.set_adm_location()
        self.update_labels()
        self.update_descriptions()
        self.set_image()
        self.set_commonscat()
        self.set_coords(("lat", "lon"))
        self.set_wd_item(self.find_matching_wikidata(mapping))
