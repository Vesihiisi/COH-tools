from Monument import Monument
import importer_utils as utils


class EeEt(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.nimi)
        self.add_label("et", name)

    def set_descriptions(self):
        short_d = {"en": "cultural property in Estonia",
                   "sv": "kulturarv i Estonia"}
        long_d = {
            "en": "cultural property in {}, Estonia",
            "sv": "kulturarv i {}, Estland"
        }
        if self.has_non_empty_attribute("omavalitsus"):
            municip = self.omavalitsus
            for language in long_d:
                self.add_description(
                    language, long_d[language].format(municip))
        else:
            for language in short_d:
                self.add_description(language, short_d[language])

    def update_heritage(self):
        if self.has_non_empty_attribute("liik"):
            special_heritage = self.liik.lower()
            glossary = self.data_files["heritage_types"]["mappings"]
            try:
                heritage = [glossary[x]["items"]
                            for x in glossary
                            if x.lower() == special_heritage]
                if len(heritage[0]) > 0:
                    self.remove_statement("heritage_status")
                    for typ in heritage[0]:
                        self.add_statement("heritage_status", typ)
            except IndexError:
                return

    def set_no(self):
        register_no = str(self.registrant_url.split("=")[-1])
        self.add_statement("estonian_monument_id", register_no)

    def set_adm_location(self):
        if self.maakond.lower() == "territoriaalmeri":
            # territorial waters - stuff like shipwrecks
            return
        try:
            municip = self.omavalitsus
            glossary = self.data_files["municipalities"]
            municip_item = [x["item"]
                            for x in glossary
                            if x["itemLabel"] == municip]
            if len(municip_item) == 0 and "vald" not in municip:
                municip = municip + " vald"
                municip_item = [x["item"]
                                for x in glossary
                                if x["itemLabel"] == municip]
            self.add_statement("located_adm", municip_item[0])
        except IndexError:
            self.add_to_report("omavalitsus", self.omavalitsus, "located_adm")

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.number)

    def set_location(self):
        location_raw = self.aadress  # very often not an address....
        wikilinks = utils.get_unique_wikilinks(location_raw)
        if len(wikilinks) == 1:
            glossary = self.data_files["settlements"]
            target_name = wikilinks[0].title
            target_item = [x["item"]
                           for x in glossary
                           if x["itemLabel"] == target_name]
            try:
                self.add_statement("location", target_item[0])
            except IndexError:
                self.add_to_report("aadress", self.aadress, "location")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_changed()
        self.set_monuments_all_id()
        self.update_labels()
        self.set_descriptions()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_commonscat()
        self.set_image("pilt")
        self.set_coords(("lat", "lon"))
        self.set_no()
        self.set_country()
        self.set_adm_location()
        self.set_heritage()
        self.update_heritage()
        self.set_is()
        self.set_location()
        self.set_wd_item(self.find_matching_wikidata(mapping))
