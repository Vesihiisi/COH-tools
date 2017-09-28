from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class GeKa(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.name)
        self.add_label("ka", name)

    def update_descriptions(self):
        desc = "cultural heritage monument in Georgia"
        self.add_description("en", desc)

    def clean_type(self):
        """
        Return a cleaned version of self.type.

        Multiple types may exist either separated by "<br />" or ",".
        Types may include NATIONAL_IMPORTANCE_STR which should be used only
        for heritage status.
        """
        raw_type = self.type.replace("<br />", ",")
        raw_type = utils.remove_markup(raw_type)
        types = [typ.strip() for typ in raw_type.split(',')]
        if self.NATIONAL_IMPORTANCE_STR in types:
            types.remove(self.NATIONAL_IMPORTANCE_STR)
        types = list(filter(None, types))  # remove empty entries
        return ', '.join(types)

    def set_special_is(self):
        """Identify a more specific instance type to use."""
        if self.has_non_empty_attribute("type"):
            clean_type = self.clean_type()
            types = self.data_files["types"]["mappings"]
            special_types = utils.get_matching_items_from_dict(
                clean_type, types)
            if len(special_types) == 1:
                self.remove_statement("is")
                self.add_statement("is", special_types[0])
            else:
                self.add_to_report(
                    "type", clean_type, "is")

    def set_adm_location(self):
        """
        Set administrative location, or location.

        The 'municipality' field contains links pointing
        at both municipalities/districts and settlements.
        Try to first match actual administrative units,
        and if that doesn't work, settlements via mapping file.
        Settlements are added as 'location'.
        """
        adm_q = None
        settlement_q = None
        adm_dic = self.data_files["admin"]
        settlement_dic = self.data_files["settlements"]
        if self.has_non_empty_attribute("municipality"):
            if utils.count_wikilinks(self.municipality) == 1:
                adm_try = utils.q_from_first_wikilink("ka", self.municipality)
                # ensure this is an administrative unit...
                if any(x['item'] == adm_try for x in adm_dic):
                    adm_q = adm_try
                # alternatively a settlement
                elif any(x['item'] == adm_try for x in settlement_dic):
                    settlement_q = adm_try
            else:
                adm_match = utils.get_item_from_dict_by_key(
                    dict_name=adm_dic,
                    search_term=self.municipality,
                    search_in="itemLabel")
                if len(adm_match) == 1:
                    adm_q = adm_match[0]
                else:
                    settlement_match = utils.get_item_from_dict_by_key(
                        dict_name=settlement_dic,
                        search_term=self.municipality,
                        search_in="itemLabel")
                    if len(settlement_match) == 1:
                        settlement_q = settlement_match[0]

            if adm_q:
                self.add_statement("located_adm", adm_q)
            if settlement_q:
                self.add_statement("location", settlement_q)
            else:
                self.add_to_report(
                    "municipality", self.municipality, "located_adm")

    def set_inception(self):
        if self.has_non_empty_attribute("date"):
            if utils.legit_year(self.date):
                inc_year = utils.package_time({"year": self.date})
                self.add_statement("inception", inc_year)
            else:
                self.add_to_report("date", self.date, "inception")

    def set_heritage(self):
        """Set the heritage status, using mapping file."""
        if self.NATIONAL_IMPORTANCE_STR in self.type:
            self.add_statement("heritage_status", self.NATIONAL_IMPORTANCE_Q)
        else:
            super().set_heritage()

    def set_address(self):
        """
        Set the street address.

        Only if the 'address' field contains a digit.
        Form the address as "$address, $municipality".
        """
        if self.has_non_empty_attribute("address"):
            if utils.contains_digit(self.address):
                address = utils.remove_markup(self.address)
                placename = utils.remove_markup(self.municipality)
                street_address = "{}, {}".format(address, placename)
                self.add_statement("located_street", street_address)
            else:
                self.add_to_report("address", self.address, "located_street")

    def set_heritage_id(self):
        self.add_statement("heritage_georgia", self.id)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.NATIONAL_IMPORTANCE_STR = "ეროვნული"
        self.NATIONAL_IMPORTANCE_Q = "Q34480057"
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_heritage()
        self.set_country()
        self.set_coords()
        self.set_adm_location()
        self.set_address()
        self.set_is()
        self.set_image()
        self.set_commonscat()
        self.set_inception()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("ge", "ka", GeKa)
    dataset.data_files = {
        "admin": "georgia_admin.json",
        "settlements": "georgia_settlements.json"
    }
    dataset.lookup_downloads = {
        "types": "ge (ka)/types"
    }
    importer.main(args, dataset)
