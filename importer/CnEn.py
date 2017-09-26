from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class CnEn(Monument):

    def set_location(self):
        """Set the Location, using linked article."""
        loc_q = None

        if self.has_non_empty_attribute("location"):
            if utils.count_wikilinks(self.location) == 1:
                loc_q = utils.q_from_first_wikilink("en", self.location)

            if loc_q is not None:
                self.add_statement("location", loc_q)
            else:
                self.add_to_report("location", self.location, "location")

    def set_adm_location(self):
        """Set the Admin Location, using the iso of the Province."""
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
            else:
                self.add_to_report("prov_iso", self.prov_iso, "located_adm")

    def update_labels(self):
        """Add labels in English and Chinese."""
        labels = {
            "en": utils.remove_markup(self.site),
            "zh": utils.get_chinese_chars(self.chinese_name)
        }
        for lang in labels:
            self.add_label(lang, labels[lang])

    def update_descriptions(self):
        e = "Major Historical and Cultural Site Protected at the National Level"
        self.add_description("en", e)

    def set_heritage_id(self):
        wlm = self.mapping["table_name"].upper()
        self.add_statement("wlm_id", "{}-{}".format(wlm, self.designation))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("en", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("designation")
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_country()
        self.set_coords()
        self.set_adm_location()
        self.set_location()
        self.set_is()
        self.set_heritage()
        self.set_image()
        self.set_commonscat()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("cn", "en", CnEn)
    dataset.data_files = {"provinces": "china_provinces.json"}
    importer.main(args, dataset)
