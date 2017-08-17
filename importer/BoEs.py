from Monument import Monument
import importer_utils as utils


class BoEs(Monument):

    def set_adm_location(self):
        adm_match = None
        if self.has_non_empty_attribute("municipio"):
            adm_match = utils.q_from_first_wikilink("es", self.municipio)
        if not adm_match:
            adm_match = utils.q_from_first_wikilink("es", self.departamento)
        if adm_match:
            self.add_statement("located_adm", adm_match)
        else:
            self.add_to_report(
                "departamento", self.departamento, "located_adm")

    def update_labels(self):
        spanish = utils.remove_markup(self.monumento)
        self.add_label("es", spanish)

    def set_monuments_all_id(self):
        self.monuments_all_id = str(self.id)

    def set_heritage_id(self):
        self.add_statement("wlm_id", str(self.id))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("en", "monumento_enlace")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_adm_location()
        self.set_is()
        self.set_heritage()
        self.set_commonscat()
        self.set_image()
        self.set_heritage_id()
        self.set_coords(("lat", "lon"))
        self.update_labels()
        self.set_wd_item(self.find_matching_wikidata(mapping))
