from dateparser.calendars.jalali import JalaliCalendar
from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class IrFa(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.name)
        self.add_label("fa", name)

    def update_descriptions(self):
        desc = "Iranian national heritage site"
        self.add_description("en", desc)

    def set_adm_location(self):
        adm_q = None
        adm_dic = self.data_files["provinces"]
        if self.has_non_empty_attribute("ISO"):
            adm_match = utils.get_item_from_dict_by_key(
                dict_name=adm_dic,
                search_term=self.ISO,
                search_in="iso")
            if len(adm_match) == 1:
                adm_q = adm_match[0]

            if adm_q:
                self.add_statement("located_adm", adm_q)
            else:
                self.add_to_report(
                    "ISO", self.ISO, "located_adm")

    def set_location(self):
        city_q = None
        city_dic = self.data_files["cities"]
        if self.has_non_empty_attribute("city"):
            adm_match = utils.get_item_from_dict_by_key(
                dict_name=city_dic,
                search_term=self.city,
                search_in="itemLabel")
            if len(adm_match) == 1:
                city_q = adm_match[0]

            if city_q:
                self.add_statement("location", city_q)
            else:
                self.add_to_report(
                    "city", self.city, "location")

    def set_heritage(self):
        """Set the heritage status, using mapping file."""
        if self.has_non_empty_attribute("registration_date"):
            iso_date = JalaliCalendar(self.registration_date).get_date()
            if iso_date:
                date_dict = utils.datetime_to_dict(
                    iso_date.get('date_obj'), "%Y%m%d")
                qualifier = {"start_time": {"time_value": date_dict}}
                heritage = self.mapping["heritage"]["item"]
                self.add_statement("heritage_status", heritage, qualifier)
        else:
            super.set_heritage()

    # check that these are always ok
    def set_address(self):
        if self.has_non_empty_attribute("address"):
            self.add_statement("located_street", self.address)

    def set_heritage_id(self):
        self.add_statement("heritage_iran", self.id)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_heritage()
        self.set_country()
        self.set_coords()
        self.set_adm_location()
        self.set_location()
        self.set_address()
        self.set_is()  # can we do it so that it only sets this if it doesn't already exist?
        self.set_image()
        self.set_commonscat()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("ir", "fa", IrFa)
    dataset.data_files = {
        "provinces": "iran_provinces.json",  # http://tinyurl.com/yd9xed2s
        "cities": "iran_cities.json"  # http://tinyurl.com/ybslxkm9
    }
    dataset.lookup_downloads = {
    }
    importer.main(args, dataset)
