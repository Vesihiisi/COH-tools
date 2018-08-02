from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class ZaEn(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.site_name)
        self.add_label("en", name)

    def set_adm_location(self):
        # print(self.magisterial_district)
        return

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("sq")
        self.set_commonscat()
        self.set_image("image")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        # self.set_no()
        # self.set_location()
        self.exists_with_prop(mapping)
        # self.print_wd()


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("za", "en", ZaEn)
    importer.main(args, dataset)
