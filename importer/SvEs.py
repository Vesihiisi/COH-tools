from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class SvEs(Monument):

    def set_adm_location(self):
        adm_q = None
        municip_dic = self.data_files["municipalities"]
        dep_dic = self.data_files["departments"]
        municip_raw = self.municipio
        iso = self.departamento_iso

        if utils.count_wikilinks(municip_raw) == 1:
            adm_q = utils.q_from_first_wikilink("es", municip_raw)
        else:
            municip_match = utils.get_item_from_dict_by_key(
                dict_name=municip_dic,
                search_in="itemLabel",
                search_term=municip_raw)
            if len(municip_match) == 1:
                adm_q = municip_match[0]

        if adm_q is None:
            dep_match = utils.get_item_from_dict_by_key(dict_name=dep_dic,
                                                        search_in="iso",
                                                        search_term=iso)
            if len(dep_match) == 1:
                adm_q = dep_match[0]

        if adm_q is not None:
            self.add_statement("located_adm", adm_q)

    def update_labels(self):
        name = utils.remove_markup(self.monumento)
        self.add_label("es", name)

    def set_heritage_id(self):
        wlm = self.mapping["table_name"].upper()
        self.add_statement("wlm_id", "{}-{}".format(wlm, self.id))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("es", "monumento_enlace")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_coords()
        self.set_is()
        self.set_country()
        self.set_coords()
        self.set_heritage()
        self.set_heritage_id()
        self.set_adm_location()
        self.set_image()
        self.set_commonscat()

        self.update_labels()
        # self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("sv", "es", SvEs)
    dataset.data_files = {"departments": "salvador_departments.json",
                          "municipalities": "salvador_municipalities.json"}
    importer.main(args, dataset)
