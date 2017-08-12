from Monument import Monument
import importer_utils as utils


class NlGemNl(Monument):

    def set_adm_location(self):
        municipal_match = [
            x["item"] for x in self.data_files["municipalities"]
            if x["value"] == self.gemcode]
        if len(municipal_match) == 1:
            self.add_statement("located_adm", municipal_match[0])
        else:
            self.add_to_report("gemcode", self.gemcode, "located_adm")

    def set_monuments_all_id(self):
        """Map which column in table to ID in monuments_all."""
        self.monuments_all_id = "{}/{}".format(self.gemcode, self.objnr)

    def set_architect(self):
        if self.has_non_empty_attribute("architect"):
            print(self.architect)
            if utils.count_wikilinks(self.architect) > 0:
                wikilinks = utils.get_wikilinks(self.architect)
                for wl in wikilinks:
                    arch_q = utils.q_from_wikipedia("nl", wl.title)
                    if arch_q:
                        self.add_statement("architect", arch_q)
                        print(arch_q)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_adm_location()
        self.set_image()
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
        self.set_architect()
