from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class AmHy(Monument):

    def set_country(self):
        """If necessary (NK), overwrite default country with Azerbaijan."""
        azerbaijan = "Q227"
        if self.has_non_empty_attribute("prov_iso"):
            if self.prov_iso.startswith("NK-"):
                self.add_statement("country", azerbaijan)
                return
        super().set_country()

    def set_adm_location(self):
        """
        Set the Admin Location.

        Use external lists, as they are not linked.
        Try to match the Municipality first (actually a hamaynk),
        and if that doesn't work, the Province via its ISO code.
        """
        com_dic = self.data_files["communities"]
        prov_dic = self.data_files["provinces"]
        adm_q = None

        adm_match = utils.get_item_from_dict_by_key(
            dict_name=com_dic,
            search_in="itemLabel",
            search_term=self.municipality)
        if len(adm_match) == 1:
            adm_q = adm_match[0]

        if adm_q is None and self.has_non_empty_attribute("prov_iso"):
            prov_match = utils.get_item_from_dict_by_key(
                dict_name=prov_dic,
                search_in="iso",
                search_term=self.prov_iso)
            if len(prov_match) == 1:
                adm_q = prov_match[0]

        if adm_q is not None:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report(
                "municipality", self.municipality, "located_adm")

    def set_commonscat(self):
        """
        Set the commons cat.

        Dataset includes many general 'cats' like 'monuments in...'
        instead of monument-specific cat, so exclude those.
        """
        if "monuments" in self.commonscat.lower():
            return
        else:
            super().set_commonscat()

    def set_heritage_id(self):
        qual_url = None
        if self.has_non_empty_attribute("registrant_url"):
            qual_url = {"described_at_url": self.registrant_url}
        self.add_statement("armenia_heritage", str(self.id), qual_url)

    def set_directions(self):
        """
        Set directions / address.

        Use street address if 'address' contains digits,
        otherwise add as directions.
        """
        if self.has_non_empty_attribute("address"):
            if utils.contains_digit(self.address):
                self.add_statement("located_street", self.address)
            else:
                monolingual = utils.package_monolingual(self.address, 'hy')
                self.add_statement("directions", monolingual)

    def update_labels(self):
        name = utils.remove_markup(self.description)
        self.add_label("hy", name)

    def update_descriptions(self):
        english = "cultural heritage monument of Armenia"
        self.add_description("en", english)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_heritage()
        self.set_country()
        self.set_adm_location()
        self.set_image()
        self.set_coords()
        self.set_commonscat()
        self.set_is()
        self.set_directions()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("am", "hy", AmHy)
    dataset.data_files = {
        "communities": "armenia_communities.json",
        "provinces": "armenia_provinces.json"}
    importer.main(args, dataset)
