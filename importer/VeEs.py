from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class VeEs(Monument):

    def set_location(self):
        locat_raw = self.ciudad.lower()
        location_dic = self.data_files["settlements"]
        locat_match = [x for x in location_dic if x[
            "itemLabel"].lower() == locat_raw]
        if len(locat_match) == 1:
            self.add_statement("location", locat_match[0]["item"])

    def set_adm_location(self):
        wikilinks = utils.get_wikilinks(self.municipio)
        # can be more than 1
        for wl in wikilinks:
            municip_q = utils.q_from_wikipedia("es", wl.title)
            if municip_q:
                self.add_statement("located_adm", municip_q)

        if not self.has_statement("located_adm"):
            state_dict = self.data_files["states"]
            state_match = [x for x in state_dict if x[
                "iso"] == self.estado_iso]
            if len(state_match) == 1:
                self.add_statement("located_adm", state_match[0]["item"])

        if not self.has_statement("located_adm"):
            self.add_to_report("municipio", self.municipio, "located_adm")

    def set_heritage_id(self):
        """
        Set WML ID.

        Will need to be enhanced with country prefix
        once there's consensus on that.
        """
        self.add_statement("wlm_id", self.id)

    def update_labels(self):
        self.add_label("es", utils.remove_markup(self.monumento))

    def set_monuments_all_id(self):
        self.monuments_all_id = self.id

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("es", "monumento_enlace")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.update_labels()
        self.set_adm_location()
        self.set_location()
        self.set_is()
        self.set_country()
        self.set_image()
        self.set_heritage()
        self.set_heritage_id()
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
        # self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("ve", "es", VeEs)
    dataset.data_files = {"states": "venezuela_states.json",
                          "settlements": "venezuela_settlements.json"}
    dataset.lookup_downloads = {}
    importer.main(args, dataset)
