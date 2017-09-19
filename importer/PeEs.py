from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class PeEs(Monument):

    def set_location(self):
        if self.has_non_empty_attribute("localidad"):
            if utils.count_wikilinks(self.localidad) == 1:
                loc_q = utils.q_from_first_wikilink("es", self.localidad)

            if loc_q is not None:
                self.add_statement("location", loc_q)

    def update_labels(self):
        spanish = utils.remove_markup(self.monumento)
        self.add_label("es", spanish)

    def update_descriptions(self):
        eng = "cultural heritage site in Peru"
        self.add_description("en", eng)

    def set_adm_location(self):
        adm_q = None
        municip_dic = self.data_files["municipalities"]
        reg_dic = self.data_files["regions"]

        municip_q = utils.q_from_first_wikilink("es", self.municipio)
        if municip_q in [x["item"] for x in municip_dic]:
            adm_q = municip_q

        if adm_q is None:
            iso = self.iso
            iso_match = utils.get_item_from_dict_by_key(dict_name=reg_dic,
                                                        search_term=iso,
                                                        search_in="iso")
            if len(iso_match) == 1:
                adm_q = iso_match[0]

        if adm_q is not None:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report("municipio", self.municipio, "located_adm")

    def set_heritage_id(self):
        wlm_prefix = self.mapping["table_name"].upper()
        self.add_statement("wlm_id", "{}-{}".format(wlm_prefix, self.id))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("es", "monumento_enlace")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_adm_location()
        self.set_country()
        self.set_location()
        self.set_heritage()
        self.set_heritage_id()
        self.set_coords()
        self.set_is()
        self.set_commonscat()
        self.set_image()
        self.update_descriptions()
        self.update_labels()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("pe", "es", PeEs)
    dataset.data_files = {
        "municipalities": "peru_provinces.json", "regions": "peru_regions.json"}
    importer.main(args, dataset)
