import dateparser
from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class HkEn(Monument):

    def set_heritage(self):
        if self.has_non_empty_attribute("declaration_date"):
            parsed_d = dateparser.parse(self.declaration_date)
            # will give None when failure
            if parsed_d:
                date_dict = utils.datetime_object_to_dict(parsed_d)
                qualifier = {"start_time": {"time_value": date_dict}}
                heritage = self.mapping["heritage"]["item"]
                self.add_statement("heritage_status", heritage, qualifier)
            else:
                super.set_heritage()
        else:
            super.set_heritage()

    def set_admin_location(self):
        hkong = "Q8646"
        self.add_statement("located_adm", hkong)

    def set_location(self):
        loc_q = None
        if utils.count_wikilinks(self.location) == 1:
            loc_q = utils.q_from_first_wikilink("en", self.location)

        if loc_q:
            self.add_statement("location", loc_q)

    def update_labels(self):
        english = utils.remove_markup(self.name)
        self.add_label("en", english)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("en", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage()
        self.set_coords()
        self.set_country()
        self.set_admin_location()
        self.set_location()
        self.set_image()
        self.update_labels()
        # self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("hk", "en", HkEn)
    importer.main(args, dataset)
