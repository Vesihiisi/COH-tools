from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class CnEn(Monument):

    def set_adm_location(self):
        adm_q = None
        if self.has_non_empty_attribute("prov_iso"):
            adm_dic = self.data_files["provinces"]
            iso = self.prov_iso
            adm_match = utils.get_item_from_dict_by_key(
                dict_name=adm_dic, search_term=iso, search_in="iso")
            if len(adm_match) == 1:
                adm_q = adm_match[0]

        if adm_q is not None:
            self.add_statement("located_adm", adm_q)

    def update_labels(self):
        site = utils.remove_markup(self.site)
        self.add_label("en", site)

        print(self.chinese_name)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("en", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("designation")
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_adm_location()
        self.set_is()
        self.set_heritage()
        self.update_labels()
        #self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("cn", "en", CnEn)
    dataset.data_files = {"provinces": "china_provinces.json"}
    importer.main(args, dataset)
