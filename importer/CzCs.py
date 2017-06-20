from Monument import Monument
import importer_utils as utils


class CzCs(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.name)
        self.add_label("cs", name)

    def update_descriptions(self):
        bases_long = {
            "en": "cultural property in {}, Czech Republic",
            "sv": "kulturarv i {}, Tjeckien"}
        bases_short = {
            "en": "cultural property in the Czech Republic",
            "sv": "kulturarv i Tjeckien"}
        if self.has_non_empty_attribute("municipality"):
            for language in bases_long:
                self.add_description(language, bases_long[
                                     language].format(self.municipality))
        else:
            for language in bases_short:
                self.add_description(language, bases_short[language])

    def set_no(self):
        code = str(self.id_objektu)
        self.add_statement("czech_monument_id", code)

    def set_monuments_all_id(self):
        self.monuments_all_id = self.id_objektu

    def set_heritage(self):
        start_raw = self.monument_since
        try:
            start = start_raw.split("-")
            start_date = {"time_value": {"year": int(
                start[0]), "month": int(start[1]), "day": int(start[2])}}
            heritage = self.mapping["heritage"]
            self.add_statement("heritage_status", heritage[
                               "item"], {"start_time": start_date})
        except ValueError:
            self.add_to_report("heritage_start_date", self.monument_since)

    def set_admin_location(self):
        if self.has_non_empty_attribute("municipality"):
            municip_dict = self.data_files["municipalities"]
            municip = self.municipality
            try:
                municip_match = [x["item"] for x in municip_dict
                                 if x["cs"].lower() == municip.lower()][0]
                self.add_statement("located_adm", municip_match)
            except IndexError:
                self.add_to_report(
                    "municipality", self.municipality, "located_adm")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.update_labels()
        self.set_commonscat()
        self.set_image("image")
        self.set_coords(("lat", "lon"))
        self.set_no()
        self.set_country()
        self.set_heritage()
        self.set_admin_location()
