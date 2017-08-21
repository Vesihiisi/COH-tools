from Monument import Monument
import importer_utils as utils


class MtDe(Monument):

    def set_adm_location(self):
        municip_raw = self.gemeinde
        municip_q = utils.q_from_wikipedia("de", municip_raw)
        if municip_q:
            self.add_statement("located_adm", municip_q)
        else:
            self.add_to_report("gemeinde", self.gemeinde, "located_adm")

    def update_labels(self):
        labels = {
            "de": self.name_de,
            "en": self.name_en,
            "mt": self.name_mt
        }
        for language in labels:
            self.add_label(language, labels[language])

    def set_monuments_all_id(self):
        self.monuments_all_id = self.inventarnummer

    def set_heritage_id(self):
        self.add_statement("malta_monument_id", self.inventarnummer)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("de", "artikel")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_heritage_id()
        self.set_image("foto")
        self.set_commonscat()
        self.set_coords(("lat", "lon"))
        self.set_is()
        self.set_heritage()
        self.update_labels()
        self.set_adm_location()
        self.set_wd_item(self.find_matching_wikidata(mapping))
