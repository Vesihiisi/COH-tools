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
            print(desc_en)

    def set_adm_location(self):
        if self.has_non_empty_attribute("freguesia"):
            parish = utils.q_from_first_wikilink("pt", self.freguesia)
            self.add_statement("located_adm", parish)

    def set_no(self):
        code = self.id
        self.add_statement("igespar_id", str(code))

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("pt")
        self.update_descriptions()
        self.set_commonscat()
        self.set_image("imagem")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_no()
        # self.set_location()
        self.exists_with_prop(mapping)
        # self.print_wd()


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("pt", "pt", PtPt)
    importer.main(args, dataset)
