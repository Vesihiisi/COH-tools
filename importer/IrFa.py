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
        self.set_from_dict_match(
            lookup_dict=self.data_files["provinces"],
            dict_label="iso",
            value_label="ISO",
            prop="located_adm"
        )

    def set_location(self):
        self.set_from_dict_match(
            lookup_dict=self.data_files["cities"],
            dict_label="itemLabel",
            value_label="city",
            prop="location"
        )

    def set_heritage(self):
        """Set the heritage status, using mapping file."""
        if self.has_non_empty_attribute("registration_date"):
            try:
                iso_date = JalaliCalendar(self.registration_date).get_date()
            except TypeError:
                print("dateparser.JalaliCalendar could not handle: {}".format(
                    self.registration_date))
                iso_date = None

            if iso_date:
                date_dict = utils.datetime_to_dict(
                    iso_date.get('date_obj'), "%Y%m%d")
                qualifier = {"start_time": utils.package_time(date_dict)}
                heritage = self.mapping["heritage"]["item"]
                self.add_statement("heritage_status", heritage, qualifier)
            else:
                self.add_to_report(
                    "registration_date", self.registration_date, "start_time")
        else:
            super().set_heritage()

    def set_directions(self):
        if self.has_non_empty_attribute("address"):
            monolingual = utils.package_monolingual(self.address, 'fa')
            self.add_statement("directions", monolingual)

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
        self.set_directions()
        self.set_is()
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
    importer.main(args, dataset)
