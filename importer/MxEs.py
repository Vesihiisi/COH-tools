from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class MxEs(Monument):

    def set_adm_location(self):
        adm_q = None
        munic_raw = self.municipio
        if utils.count_wikilinks(munic_raw) == 1:
            adm_q = utils.q_from_first_wikilink("es", munic_raw)

        if adm_q:
            self.add_statement("located_adm", adm_q)

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
        self.set_is()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("mx", "es", MxEs)
    dataset.data_files = {}
    importer.main(args, dataset)
