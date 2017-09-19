from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class PtPt(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.designacoes)
        self.add_label("pt", name)

    def update_descriptions(self):
        if self.has_non_empty_attribute("freguesia"):
            freg = utils.remove_markup(self.freguesia)
            desc_en = "heritage site in " + freg + ", Portugal"
            self.add_description("en", desc_en)

    def set_adm_location(self):
        adm_q = None
        distr_dic = self.data_files["districts"]
        freguesia_dic = self.data_files["freguesias"]

        if self.has_non_empty_attribute("freguesia"):
            parish_q = utils.q_from_first_wikilink("pt", self.freguesia)
            if parish_q in [x["item"] for x in freguesia_dic]:
                adm_q = parish_q

        if adm_q is None:
            iso = self.region_iso
            reg_match = utils.get_item_from_dict_by_key(dict_name=distr_dic,
                                                        search_in="iso",
                                                        search_term=iso)
            if len(reg_match) == 1:
                adm_q = reg_match[0]

        if adm_q is not None:
            self.add_statement("located_adm", adm_q)

    def set_heritage_id(self):
        self.add_statement("igespar_id", str(self.id))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("pt", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_country()
        self.set_adm_location()
        self.set_coords()
        self.set_is()
        self.set_commonscat()
        self.set_image("imagem")
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("pt", "pt", PtPt)
    dataset.data_files = {"freguesias": "portugal_freguesias.json",
                          "districts": "portugal_disctricts.json"}
    importer.main(args, dataset)
