from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class BeBruNl(Monument):

    def set_adm_location(self):
        brussel_region = "Q240"
        location = self.plaats
        municip_dict = self.data_files["municipalities"]
        if location:
            location_match = utils.get_item_from_dict_by_key(
                dict_name=municip_dict,
                search_term=location,
                search_in="itemLabel")
            if len(location_match) == 1:
                self.add_statement("located_adm", location_match[0])
            else:
                self.add_to_report("plaats", self.plaats, "located_adm")
        else:
            self.add_statement("located_adm", brussel_region)

    def set_heritage(self):
        """
        Set heritage status with or without start date.

        If possible to parse the date of when
        the heritage status was assigned, add it
        as qualifier to the heritage status property.
        Otherwise, add default heritage status
        without start date.
        """
        if self.has_non_empty_attribute("beschermd"):
            prot_date = self.beschermd
            try:
                date_dict = utils.date_to_dict(prot_date, "%d/%m/%Y")
                qualifier = {"start_time": utils.package_time(date_dict)}
                heritage = self.mapping["heritage"]["item"]
                self.add_statement("heritage_status", heritage, qualifier)
            except ValueError:
                self.add_to_report(
                    "beschermd", self.beschermd, "heritage_status")
                return super().set_heritage()
        else:
            return super().set_heritage()

    def set_address_and_disambig(self):
        street_with_no = utils.remove_markup(self.adres.title()).rstrip(',')

        # strip "0" as the number
        streets = [street.partition(' 0')[0]
                   for street in street_with_no.split(', ')]
        street_with_non_zero_no = ', '.join(streets)

        whole_address = "{}, {}".format(street_with_non_zero_no, self.plaats)
        qualifier = {"language of name": "Q7411"}  # in dutch
        self.add_statement("located_street", whole_address, qualifier)

        self.add_disambiguator(street_with_non_zero_no, 'nl')

    def set_special_is(self):
        objtype = self.objtype.lower()
        types = self.data_files["type"]["mappings"]
        special_types = utils.get_matching_items_from_dict(objtype, types)
        if len(special_types) > 0:
            for q in special_types:
                self.add_statement("is", q)

    def set_style(self):
        if self.has_non_empty_attribute("bouwstijl"):
            style_raw = self.bouwstijl.lower()
            styles = self.data_files["style"]["mappings"]
            arch_style = utils.get_matching_items_from_dict(style_raw, styles)
            if len(arch_style) > 0:
                for q in arch_style:
                    self.add_statement("architectural_style", q)
            else:
                self.add_to_report(
                    "bouwstijl", self.bouwstijl, "architectural_style")

    def set_architect(self):
        if self.has_non_empty_attribute("bouwdoor"):
            if utils.count_wikilinks(self.bouwdoor) == 1:
                arch_q = utils.q_from_first_wikilink("nl", self.bouwdoor)
                self.add_statement("architect", arch_q)
            else:
                self.add_to_report("bouwdoor", self.bouwdoor, "architect")

    def update_labels(self):
        dutch = utils.remove_markup(self.omschrijving)
        self.add_label("nl", dutch)

    def update_descriptions(self):
        dutch = "{} in {}, België".format(self.objtype.lower(), self.plaats)
        self.add_description("nl", dutch)

    def set_building_year(self):
        if self.has_non_empty_attribute("bouwjaar"):
            if utils.legit_year(self.bouwjaar):
                self.add_statement(
                    "inception", utils.package_time({"year": self.bouwjaar}))
            else:
                self.add_to_report("bouwjaar", self.bouwjaar, "inception")

    def set_heritage_id(self):
        self.add_statement("heritage_brussels", self.code)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("code")
        self.set_changed()
        self.set_wlm_source()
        self.set_source()
        self.set_registrant_url()
        self.set_heritage_id()
        self.set_heritage()
        self.set_country()
        self.set_image()
        self.set_adm_location()
        self.set_commonscat()
        self.set_architect()
        self.set_style()
        # self.set_is()
        self.set_special_is()
        self.set_coords()
        self.set_building_year()
        self.set_address_and_disambig()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("be-bru", "nl", BeBruNl)
    dataset.data_files = {"municipalities": "belgium_municipalities.json"}
    dataset.lookup_downloads = {"type": "be-bru (nl)/objtype",
                                "style": "be-bru (nl)/bouwstijl"}
    importer.main(args, dataset)
