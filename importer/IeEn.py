from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class IeEn(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.name)
        self.add_label("en", name)

    def set_adm_location(self):
        counties = self.data_files["counties"]
        try:
            county_name = "County " + self.county
            county_item = [x["item"]
                           for x in counties if x["en"] == county_name]
            ref = self.create_wlm_source()
            self.add_statement("located_adm", county_item[0], refs=[ref])
        except IndexError:
            return

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("en")
        self.set_commonscat()
        self.set_image("image")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        # self.set_no()
        # self.set_location()
        # self.exists_with_prop(mapping)
        self.print_wd()


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("ie", "en", IeEn)
    dataset.data_files = {
        "counties": "ireland_counties.json"
    }
    importer.main(args, dataset)
