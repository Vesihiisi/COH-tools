from Monument import Monument
import importer_utils as utils


MAPPING_DIR = "mappings"


class NoNo(Monument):

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
        self.add_statement("norwegian_monument_id", str(self.id))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("no", "monument_article")

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.id)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.update_labels()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_image("bilde")
        self.set_commonscat()
        self.set_coords(("lat", "lon"))
        self.set_no()
        # self.set_adm_location()
        # self.set_location()
        # self.set_sagsnr()
        self.print_wd()
        self.set_wd_item(self.find_matching_wikidata(mapping))
