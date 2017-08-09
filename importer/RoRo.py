from Monument import Monument


class RoRo(Monument):

    def set_adm_location(self):
        counties = self.data_files["counties"]
        adm_code = self.judetul_iso
        county_item = [x["item"] for x in counties if x["iso_code"] == adm_code]
        try:
            self.add_statement("located_adm", county_item[0])
        except IndexError:
            self.add_to_report("judetul_iso", self.judetul_iso, prop_name = "located_adm")

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.cod)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("ro", "monument_article")

    def set_wlm_id(self):
        """
        Set the WLM ID.

        Do _not_ use the Romania LMI code (P1770)
        as it's made up and has no relevance to the
        real world.
        """
        self.add_statement("wlm_id", self.cod)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_heritage()
        self.set_country()
        self.set_source()
        self.set_wlm_id()
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
        self.set_image("imagine")
        self.set_adm_location()
