from Monument import Monument


class RoRo(Monument):

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.cod)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("ro", "monument_article")

    def set_heritage_id(self):
        """Set Romania heritage ID, P1770."""
        self.add_statement("romanian_monument_id", self.cod)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_heritage()
        self.set_country()
        self.set_source()
        self.set_heritage_id()
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
        self.set_image("imagine")
