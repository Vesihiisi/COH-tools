from Monument import Monument


class ClEs(Monument):

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.id)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_heritage()
        self.set_country()
        self.set_source()
        # self.set_wlm_id()
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
        self.set_image("imagen")
        # self.set_adm_location()
        self.print_wd()
