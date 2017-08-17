from Monument import Monument
import importer_utils as utils


class CoEs(Monument):

    def update_descriptions(self):
        descs = {
            "en": "national monument of Colombia",
            "es": "Monumento Nacional de Colombia"
        }
        for lg in descs:
            self.add_description(lg, descs[lg])

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.id)

    def update_labels(self):
        spanish = utils.remove_markup(self.monumento)
        self.add_label("es", spanish)

    def set_adm_location(self):
        match = None
        dep_dic = self.data_files["departments"]
        if self.has_non_empty_attribute("municipio"):
            match = utils.q_from_first_wikilink("es", self.municipio)
        else:
            dep_match = [x for x in dep_dic if x["iso"] == self.iso]
            if len(dep_match) == 1:
                match = dep_match[0]["item"]
        if match:
            self.add_statement("located_adm", match)
        else:
            self.add_to_report("municipio", self.municipio, "located_adm")

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("es", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_heritage()
        self.set_country()
        self.set_source()
        self.set_registrant_url()
        self.set_is()
        self.set_adm_location()
        self.set_image("imagen")
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))
