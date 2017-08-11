from Monument import Monument
import importer_utils as utils


class ClEs(Monument):

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.id)

    def set_adm_location(self):
        adm_location_q = False
        municip_dict = self.data_files["municipalities"]
        region_dict = self.data_files["regions"]
        if utils.count_wikilinks(self.comuna) == 1:
            comuna_q = (utils.q_from_first_wikilink("es", self.comuna))
            comuna_match = [x for x in municip_dict if x["item"] == comuna_q]
            if len(comuna_match) == 1:
                adm_location_q = comuna_q
            else:
                region_iso_match = [x["item"]
                                    for x in region_dict
                                    if x["iso_code"] == self.ISO]
                if len(region_iso_match) == 1:
                    adm_location_q = region_iso_match[0]
        if adm_location_q:
            self.add_statement("located_adm", adm_location_q)
        else:
            self.add_to_report("comuna", self.comuna, "located_adm")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_heritage()
        self.set_country()
        self.set_source()
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
        self.set_image("imagen")
        self.set_adm_location()
        # self.print_wd()
