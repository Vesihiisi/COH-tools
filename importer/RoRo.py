from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class RoRo(Monument):

    def set_adm_location(self):
        counties = self.data_files["counties"]
        self.set_from_dict_match(counties, "iso_code",
                                 "judetul_iso", "located_adm")

    def set_location(self):
        """
        Set Location property from article linked in localitate.

        Run this after set_adm_location. localitate can
        contain several links (we take the 1st which seems to
        be the most granular one) and a mix of administrative
        types. Compare with admin location so that they're not
        the same.
        """
        if self.has_non_empty_attribute("localitate"):
            loc_item = None
            if utils.count_wikilinks(self.localitate) > 0:
                loc_link = utils.get_wikilinks(self.localitate)[0]
                loc_item = utils.q_from_wikipedia("ro", loc_link.title)
                adm_item = self.get_statement_values("located_adm")
                if loc_item and loc_item != adm_item[0]:
                    self.add_statement("location", loc_item)

            if not loc_item:
                self.add_to_report("localitate", self.localitate, "location")

    def set_heritage_id(self):
        self.add_statement("romanian_monument_id", self.cod)

    def update_descriptions(self):
        adm_code = self.judetul_iso
        counties = self.data_files["counties"]
        county_item = utils.get_item_from_dict_by_key(dict_name=counties,
                                                      search_term=adm_code,
                                                      return_content_of="itemLabel",
                                                      search_in="iso_code")
        if len(county_item) == 1:
            place_name = "{}, Romania".format(county_item[0])
        else:
            place_name = "Romania"
        desc = "heritage site in {}".format(place_name)
        self.add_description("en", desc)
        self.add_disambiguator(str(self.cod))

    def set_address(self):
        street_patterns = ("piața", "str.", "bd.")
        if self.has_non_empty_attribute("adresa"):
            adr_lower = self.adresa.lower()
            adr_nice = utils.remove_markup(self.adresa)
            if any(pattern in adr_lower for pattern in street_patterns):
                if self.has_non_empty_attribute("localitate"):
                    town = utils.remove_markup(self.localitate)
                    adr_nice = "{}, {}".format(adr_nice, town)
                self.add_statement("located_street", adr_nice)
            else:
                directions = utils.package_monolingual(adr_nice, 'ro')
                self.add_statement("directions", directions)

    def update_labels(self):
        romanian = utils.remove_markup(self.denumire)
        self.add_label("ro", romanian)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("cod")
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_heritage()
        self.set_country()
        self.set_adm_location()
        self.set_address()
        self.set_location()
        self.set_coords()
        self.set_commonscat()
        self.set_image("imagine")
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("ro", "ro", RoRo)
    dataset.data_files = {"counties": "romania_counties.json"}
    importer.main(args, dataset)
