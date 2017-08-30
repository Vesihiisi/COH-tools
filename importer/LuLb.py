from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class LuLb(Monument):

    def set_adm_location(self):
        adm_q = None
        dis_dic = self.data_files["districts"]
        if self.has_non_empty_attribute("region_iso"):
            dis_raw = self.region_iso.lower()
            dis_match = [x for x in dis_dic if x[
                "iso"].lower() == dis_raw]
            if len(dis_match) == 1:
                adm_q = dis_match[0]["item"]
        if adm_q:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report("region-iso", self.region_iso, "located_adm")

    def update_labels(self):
        lb = utils.remove_markup(self.offiziellen_numm)
        self.add_label("lb", lb)

    def set_heritage_id(self):
        """Set WLM ID with country's ISO-prefix."""
        ccode = self.mapping["country_code"].upper()
        id_no = "{}-{}".format(ccode, self.id)
        self.add_statement("wlm_id", id_no)

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = self.id

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("lb", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_adm_location()
        self.set_is()
        self.set_heritage()
        self.set_heritage_id()
        self.update_labels()
        # self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("lu", "lb", LuLb)
    dataset.data_files = {"districts": "luxembourg_districts.json"}
    dataset.lookup_downloads = {}
    importer.main(args, dataset)
