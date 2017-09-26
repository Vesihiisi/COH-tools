from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class MxEs(Monument):

    def set_location(self):
        """Set the Location, using linked 'localidad'."""
        loc_q = None
        loc_raw = self.localidad
        if utils.count_wikilinks(loc_raw) == 1:
            loc_q = utils.q_from_first_wikilink("es", loc_raw)

        if loc_q:
            self.add_statement("location", loc_q)

    def set_adm_location(self):
        """
        Set the Admin Location.

        Try to use a linked 'municipio',
        and if that doesn't work, resolve the state
        via its iso code.
        """
        adm_q = None
        munic_raw = self.municipio
        state_dic = self.data_files["states"]

        if utils.count_wikilinks(munic_raw) == 1:
            adm_q = utils.q_from_first_wikilink("es", munic_raw)

        if adm_q is None:
            iso = self.iso
            state_match = utils.get_item_from_dict_by_key(dict_name=state_dic,
                                                          search_in="iso",
                                                          search_term=iso)
            if len(state_match) == 1:
                adm_q = state_match[0]

        if adm_q is not None:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report("municipio", self.municipio, "located_adm")

    def set_heritage_id(self):
        self.add_statement("wlm_id", str(self.id))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("es", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_heritage()
        self.set_image("imagen")
        self.set_commonscat("monumento_categoria")
        self.set_coords()
        self.set_country()
        self.set_adm_location()
        self.set_location()
        self.set_is()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("mx", "es", MxEs)
    dataset.data_files = {"states": "mexico_states.json"}
    importer.main(args, dataset)
