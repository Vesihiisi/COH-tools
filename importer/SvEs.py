from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class SvEs(Monument):

    def set_heritage(self):
        """
        Set the Heritage Status.

        Based on:
        https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/sv_(es)/tipo
        If no special status found, resort to defaults from mapping.
        """
        her_dic = self.data_files["heritage_type"]["mappings"]
        her_raw = self.tipo

        her_match = utils.get_matching_items_from_dict(her_raw, her_dic)
        if len(her_match) == 1:
            heritage = her_match[0]
            self.add_statement("heritage_status", heritage)
        else:
            super().set_heritage()

    def set_adm_location(self):
        """
        Set the Admin Location.

        Try a linked Municipality first,
        then unlinked Municipality.
        If failed, use the Department iso code.
        """
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
            self.add_to_report("municipio", municip_raw, "located_adm")
            dep_match = utils.get_item_from_dict_by_key(
                dict_name=dep_dic,
                search_in="iso",
                search_term=iso)
            if len(dep_match) == 1:
                adm_q = dep_match[0]
            else:
                self.add_to_report("departamento_iso", iso, "located_adm")

        if adm_q is not None:
            self.add_statement("located_adm", adm_q)

    def update_labels(self):
        name = utils.remove_markup(self.monumento)
        self.add_label("es", name)

    def update_descriptions(self):
        eng = "cultural heritage site in El Salvador"
        self.add_description("en", eng)

    def set_directions(self):
        if self.has_non_empty_attribute("direccion"):
            monolingual = utils.package_monolingual(
                utils.remove_markup(self.direccion), 'es')
            self.add_statement("directions", monolingual)

    def set_heritage_id(self):
        wlm = "{}-{}".format(self.mapping["table_name"].upper(), self.id)
        self.add_statement("wlm_id", wlm)
        self.add_disambiguator(str(self.id))

    def exists_with_monument_article(self, language):
        return self.get_multi_param_monument_article(
            raw="monumento_enlace",
            linked="monumento",
            blocks="enlace",
            language=language)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_coords()
        self.set_is()
        self.set_country()
        self.set_coords()
        self.set_heritage()
        self.set_heritage_id()
        self.set_adm_location()
        self.set_directions()
        self.set_image()
        self.set_commonscat()
        self.update_descriptions()
        self.update_labels()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("sv", "es", SvEs)
    dataset.lookup_downloads = {"heritage_type": "sv_(es)/tipo"}
    dataset.data_files = {
        "departments": "salvador_departments.json",
        "municipalities": "salvador_municipalities.json"
    }
    importer.main(args, dataset)
