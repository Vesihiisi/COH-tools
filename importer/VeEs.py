from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class VeEs(Monument):

    def set_location(self):
        match_q = None
        if self.has_non_empty_attribute("ciudad"):
            locat_raw = self.ciudad.lower()
            location_dic = self.data_files["settlements"]
            locat_match = [x["item"] for x in location_dic
                           if x["itemLabel"].lower() == locat_raw]
            if len(locat_match) == 1:
                match_q = locat_match[0]

            if match_q:
                self.add_statement("location", match_q)
            else:
                self.add_to_report("ciudad", self.ciudad, "location")

    def set_adm_location(self):
        """
        Set the Admin Location.

        Use the linked Municipality first then fall back on state iso code,
        which is a bigger unit.
        """
        adm_q = utils.q_from_first_wikilink("es", self.municipio)

        if adm_q is None:
            self.add_to_report("municipio", self.municipio, "located_adm")
            iso_match = utils.get_item_from_dict_by_key(
                dict_name=self.data_files["states"],
                search_term=self.estado_iso,
                search_in="iso")
            if len(iso_match) == 1:
                adm_q = iso_match[0]
            else:
                self.add_to_report(
                    "estado_iso", self.estado_iso, "located_adm")

        if adm_q:
            self.add_statement("located_adm", adm_q)

    def set_heritage_id(self):
        wlm = "{}-{}".format(self.mapping["table_name"].upper(), self.id)
        self.add_statement("wlm_id", wlm)
        self.add_disambiguator(str(self.id))

    def set_directions(self):
        if self.has_non_empty_attribute("direccion"):
            monolingual = utils.package_monolingual(
                utils.remove_markup(self.direccion), 'es')
            self.add_statement("directions", monolingual)

    def update_labels(self):
        spanish = utils.remove_markup(self.monumento)
        self.add_label("es", spanish)

    def update_descriptions(self):
        desc = "national historical monument of Venezuela"
        if self.has_non_empty_attribute("ciudad"):
            desc = desc + " in {}".format(utils.remove_markup(self.ciudad))
        self.add_description("en", desc)

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
        self.set_adm_location()
        self.set_directions()
        self.set_location()
        self.set_is()
        self.set_country()
        self.set_image()
        self.set_heritage()
        self.set_heritage_id()
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("ve", "es", VeEs)
    dataset.data_files = {
        "states": "venezuela_states.json",
        "settlements": "venezuela_settlements.json"
    }
    importer.main(args, dataset)
