from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class PaEs(Monument):

    def set_adm_location(self):
        adm_q = None
        prov_dic = self.data_files["provinces"]
        iso = self.prov_iso
        prov_match = utils.get_item_from_dict_by_key(dict_name=prov_dic,
                                                     search_term=iso,
                                                     search_in="iso")
        if len(prov_match) == 1:
            adm_q = prov_match[0]

        if adm_q is not None:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report(
                "province-iso", self.province_iso, "located_adm")

    def update_labels(self):
        self.add_label("es", utils.remove_markup(self.nombre))

    def set_heritage_id(self):
        wlm_code = self.mapping["table_name"].upper()
        heritage = "{}-{}".format(wlm_code, self.id)
        self.add_statement("wlm_id", heritage)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("es", "articulo")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage()
        self.set_country()
        self.set_adm_location()
        self.set_heritage_id()
        self.set_is()
        self.set_commonscat()
        self.set_coords()
        self.set_image("imagen")
        self.update_labels()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("pa", "es", PaEs)
    dataset.data_files = {"provinces": "panama_provinces.json"}
    importer.main(args, dataset)
