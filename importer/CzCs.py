from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class CzCs(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.name)
        self.add_label("cs", name)

    def set_adm_location(self):
        """
        Set the administrative location.

        TODO
        Download all
        """
        print(self.municipality)

    def set_no(self):
        code = str(self.id_objektu)
        self.add_statement("czech_monument_id", code)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("sq")
        self.set_commonscat()
        self.set_image("image")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_no()
        # self.set_location()
        self.exists_with_prop(mapping)
        # self.print_wd()


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("cz", "cs", CzCs)
    importer.main(args, dataset)
