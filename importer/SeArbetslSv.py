from Monument import Monument
import importer_utils as utils


class SeArbetslSv(Monument):

    def set_descriptions(self):
        DESC_BASES = {"sv": "arbetslivsmuseum", "en": "museum"}
        for language in ["en", "sv"]:
            self.add_description(language, DESC_BASES[language])

    def add_location_to_desc(self, language, municipality):
        if language == "sv":
            self.wd_item["descriptions"][language] += " i " + municipality
        elif language == "en":
            self.wd_item["descriptions"][
                language] += " in " + municipality + ", Sweden"

    def set_adm_location(self):
        municip_dict = self.data_files["municipalities"]
        if self.kommun == "Göteborg":
            municip_name = "Gothenburg"
        else:
            municip_name = self.kommun
        pattern = municip_name.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "en"].lower() == pattern][0]
            self.add_statement("located_adm", municipality)
            swedish_name = [x["sv"]
                            for x in municip_dict
                            if x["item"] == municipality][0]
            english_name = [x["en"]
                            for x in municip_dict
                            if x["item"] == municipality][0]
            self.add_location_to_desc("sv", swedish_name)
            self.add_location_to_desc("en", english_name)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.kommun))
            return

    def set_type(self):
        if self.has_non_empty_attribute("typ"):
            table = self.data_files["types"]["mappings"]
            type_to_search_for = self.typ.lower()
            try:
                special_type = [table[x]["items"]
                                for x in table
                                if x.lower() == type_to_search_for][0]
                self.substitute_statement("is", special_type)
            except IndexError:
                return
        return

    def set_location(self):
        settlements_dict = self.data_files["settlements"]
        if self.has_non_empty_attribute("ort"):
            try:
                location = [x["item"] for x in settlements_dict if x[
                    "sv"].strip() == utils.remove_markup(self.ort)][0]
                self.add_statement("location", location)
            except IndexError:
                return

    def set_id(self):
        if self.has_non_empty_attribute("id"):
            self.add_statement("arbetsam", self.id)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.set_labels("sv", self.namn)
        self.set_descriptions()
        self.set_id()
        self.set_type()
        self.set_adm_location()
        self.set_location()
        self.exists("sv", "monument_article")
        self.set_image("bild")
        self.set_commonscat()
        self.set_coords(("lat", "lon"))
        self.exists_with_prop(mapping)
