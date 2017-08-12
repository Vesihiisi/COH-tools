from Monument import Monument
import importer_utils as utils


class NlGemNl(Monument):

    def set_adm_location(self):
        municipal_match = [
            x["item"] for x in self.data_files["municipalities"]
            if x["value"] == self.gemcode]
        if len(municipal_match) == 1:
            self.add_statement("located_adm", municipal_match[0])
        else:
            self.add_to_report("gemcode", self.gemcode, "located_adm")

    def set_monuments_all_id(self):
        """Map which column in table to ID in monuments_all."""
        self.monuments_all_id = "{}/{}".format(self.gemcode, self.objnr)

    def set_architect(self):
        if self.has_non_empty_attribute("architect"):
            if utils.count_wikilinks(self.architect) > 0:
                wikilinks = utils.get_wikilinks(self.architect)
                for wl in wikilinks:
                    arch_q = utils.q_from_wikipedia("nl", wl.title)
                    if arch_q:
                        self.add_statement("architect", arch_q)

    def set_inception(self):
        if (self.has_non_empty_attribute("bouwjaar") and
           utils.legit_year(self.bouwjaar)):
            self.add_statement(
                "inception", {"time_value": {"year": self.bouwjaar}})

    def set_address(self):
        street_address = False
        if self.has_non_empty_attribute("adres"):
            if len(utils.wparser.parse(self.adres).filter_templates()) == 1:
                address_try = utils.wparser.parse(
                    self.adres).filter_templates()[0].params[0]
                if utils.contains_digit(address_try):
                    street_address = address_try
            else:
                if utils.contains_digit(self.adres):
                    street_address = self.adres
        if street_address:
            self.add_statement("located_street", street_address)

    def set_heritage_id(self):
        self.add_statement("wlm_id", self.monuments_all_id)

    def update_labels(self):
        label = utils.remove_markup(self.object)
        label = self.add_label("nl", label)

    def update_descriptions(self):
        desc_dict = {
            "nl": "gemeentelijk monument in {}",
            "fy": "gemeentlik monumint yn {}",
            "en": "municipal monument in {}"
        }
        placenames = {
        "en": "the Netherlands", "nl":"Nederland", "fy":"Nederlân"
        }
        for lang in desc_dict:
            try:
                placename = [x[lang] for x
                                   in self.data_files["municipalities"]
                                   if x["value"] == self.gemcode][0]
            except (KeyError, IndexError):
                placename = placenames[lang]
            self.add_description(lang, desc_dict[lang].format(placename))

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_heritage_id()
        self.update_labels()
        self.update_descriptions()
        self.set_country()
        self.set_adm_location()
        self.set_image()
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
        self.set_architect()
        self.set_inception()
        self.set_address()
        self.set_wd_item(self.find_matching_wikidata(mapping))
