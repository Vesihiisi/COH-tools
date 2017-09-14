from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class UyEs(Monument):

    def set_location(self):
        loc_dic = self.data_files["settlements"]
        loc_q = None

        if self.has_non_empty_attribute("localidad"):
            loc_raw = self.localidad
            if utils.count_wikilinks(loc_raw) == 1:
                loc_try = utils.q_from_first_wikilink("es", loc_raw)
                if loc_try in [x["item"] for x in loc_dic]:
                    loc_q = loc_try
            else:
                loc_try = utils.q_from_wikipedia("es", loc_raw)
                if loc_try in [x["item"] for x in loc_dic]:
                    loc_q = loc_try

            if loc_q:
                self.add_statement("location", loc_q)
            else:
                self.add_to_report("localidad", self.localidad, "location")

    def set_adm_location(self):
        dep_dic = self.data_files["departments"]
        iso = self.dep_iso
        dep_match = utils.get_item_from_dict_by_key(
            dict_name=dep_dic,
            search_in="iso",
            search_term=iso)
        if len(dep_match) == 1:
            adm_q = dep_match[0]

        if adm_q:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report("dep_iso", self.dep_iso, "located_adm")

    def set_wd_item_via_name(self):
        if utils.count_wikilinks(self.monumento) == 1:
            monum_q = utils.q_from_first_wikilink("es", self.monumento)
            self.set_wd_item(monum_q)

    def update_labels(self):
        es_name = utils.remove_markup(self.monumento)
        self.add_label("es", es_name)

    def update_descriptions(self):
        en = "cultural heritage monument of Uruguay"
        self.add_description("en", en)

    def set_heritage_id(self):
        wlm_code = self.mapping["table_name"].upper()
        self.add_statement("wlm_id", "{}-{}".format(wlm_code, self.id))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("es", "monumento_enlace")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_adm_location()
        self.set_location()
        self.set_is()
        self.set_heritage()
        self.set_coords()
        self.set_image()
        self.set_heritage_id()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item_via_name()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("uy", "es", UyEs)
    dataset.data_files = {"departments": "uruguay_departments.json",
                          "settlements": "uruguay_settlements.json"}
    importer.main(args, dataset)
