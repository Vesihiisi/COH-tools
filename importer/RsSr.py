from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class RsSr(Monument):

    def set_address(self):
        """
        Set address / directions.

        Address, with attached city, if there's digits in it.
        Otherwise directions.
        """
        if self.has_non_empty_attribute("address"):
            if utils.contains_digit(self.address):
                if self.has_non_empty_attribute("city"):
                    city_no_brackets = utils.get_rid_of_brackets(self.city)
                    address = "{}, {}".format(self.address, city_no_brackets)
                else:
                    address = self.address
                self.add_statement("located_street", address)
            else:
                dirs = utils.package_monolingual("sr", self.address)
                self.add_statement("directions", dirs)

    def set_location(self):
        """
        Set location property.

        'City' is never wikilinked, so try to match
        against list of known settlements.
        """
        self.set_from_dict_match(
            lookup_dict=self.data_files["settlements"],
            dict_label="itemLabel",
            value_label="city",
            prop="location")

    def set_adm_location(self):
        """
        Set administrative location.

        If possible, match district / municipality.
        Not wikilinked, and contain a mix of various
        types, so match against list of all administrative
        units.
        If that doesn't work, resort to okrug via iso.
        """
        adm_q = None
        adm_dic = self.data_files["admin"]
        okr_dic = self.data_files["okruzi"]

        municip_try = utils.get_item_from_dict_by_key(
            dict_name=adm_dic,
            search_in="itemLabel",
            search_term=self.district)
        if len(municip_try) == 1:
            adm_q = municip_try[0]
        else:
            self.add_to_report("district", self.district, "located_adm")

        if not adm_q and self.has_non_empty_attribute("iso_okrug"):
            iso_try = utils.get_item_from_dict_by_key(
                dict_name=okr_dic,
                search_in="iso",
                search_term=self.iso_okrug)
            if len(iso_try) == 1:
                adm_q = iso_try[0]
            else:
                self.add_to_report("iso_okrug", self.iso_okrug, "located_adm")

        if adm_q:
            self.add_statement("located_adm", adm_q)

    def update_descriptions(self):
        descs = {
            "en": "protected cultural monument in Serbia",
            "nl": "beschermd monument in Servië",
            "ru": "охраняемый памятник культуры в Сербии",
            "sr": "заштићен споменик културе у Србији",
        }
        for lang, desc in descs.items():
            self.add_description(lang, desc)

    def update_labels(self):
        name = utils.remove_markup(self.name)
        self.add_label("sr", name)

    def set_heritage_id(self):
        self.add_statement("serbia_heritage_id", self.id)
        self.add_disambiguator(self.id)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_location()
        self.set_adm_location()
        self.set_address()
        self.set_is()
        self.set_heritage()
        self.set_heritage_id()
        self.update_labels()
        self.update_descriptions()
        self.set_coords()
        self.set_image()
        self.set_commonscat()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("rs", "sr", RsSr)
    dataset.data_files = {"admin": "serbia_admin.json",
                          "okruzi": "serbia_okruzi.json",
                          "settlements": "serbia_settlements.json"}
    importer.main(args, dataset)
