from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class NoNo(Monument):
    """
    A class to process monuments_no_(no).

    TODO.
    there's an API:
    https://data.norge.no/data/riksantikvaren/kulturminnes%C3%B8k
    look into how we can benefit from it!
    """

    def update_labels(self):
        """
        Set the labels.

        NOTE
        Some of these are in all caps or have multiple spaces:
        UTSIRA FYRSTASJON
        SØGARD FJONE  -  FJONE SØNDRE
        VÅLE PRESTEGÅRD, museum

        TODO
        *Normalize - to title case?
            It contains some old-style numbers, and these will be broken:
            XXVIII -> Xxviii

        * rm extra whitespace
        """
        for part in self.navn.split(" "):
            if part.isupper():
                print(part, "----", part.capitalize())

    def set_no(self):
        self.add_statement("norwegian_monument_id", self.id)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("no")
        self.set_commonscat()
        self.set_image("bilde")
        self.set_coords(("lat", "lon"))
        self.set_no()
        # self.set_adm_location()
        # self.set_location()
        # self.set_sagsnr()
        # self.set_address()
        # self.set_inception()
        self.exists_with_prop(mapping)
        self.print_wd()


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("no", "no", NoNo)
    importer.main(args, dataset)
