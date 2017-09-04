from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class CaFr(Monument):

    def set_address(self):
        town_string = None
        if self.has_non_empty_attribute("adresse"):
            if self.has_non_empty_attribute("municipalite"):
                town_string = utils.remove_markup(self.municipalite)
            if town_string is not None:
                street_string = "{}, {}".format(self.adresse, town_string)
            else:
                street_string = self.adresse
            self.add_statement("located_street", street_string)

    def set_location(self):
        if self.has_non_empty_attribute("lieu"):
            loc_raw = self.lieu
            if utils.count_wikilinks(loc_raw) == 1:
                loc_q = utils.q_from_first_wikilink("fr", loc_raw)
                if loc_q is not None:
                    self.add_statement("location", loc_q)
                else:
                    self.add_to_report("lieu", self.lieu, "location")
            else:
                self.add_to_report("lieu", self.lieu, "location")

    def set_adm_location(self):
        adm_q = None
        municip_raw = self.municipalite
        adm_q = utils.q_from_first_wikilink("fr", municip_raw)

        if adm_q is None:
            self.add_to_report(
                "municipalite", self.municipalite, "located_adm")
            if self.has_non_empty_attribute("prov_iso"):
                prov_raw = self.prov_iso
                prov_match = [x for x in self.data_files[
                    "provinces"] if x["iso"] == prov_raw]
                if len(prov_match) == 1:
                    adm_q = prov_match[0]["item"]
                else:
                    self.add_to_report(
                        "prov_iso", self.prov_iso, "located_adm")
            else:
                self.add_to_report("prov_iso", self.prov_iso, "located_adm")

        if adm_q:
            self.add_statement("located_adm", adm_q)

    def set_inception(self):
        if self.has_non_empty_attribute("construction"):
            if utils.legit_year(self.construction):
                year = {"time_value": {"year": self.construction}}
                self.add_statement("inception", year)
            else:
                self.add_to_report(
                    "construction", self.construction, "inception")

    def set_heritage_id(self):
        self.add_statement("canadian_register", str(self.numero))

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.numero)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("fr", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_heritage_id()
        self.set_heritage()
        self.set_country()
        self.set_adm_location()
        self.set_location()
        self.set_address()
        self.set_is()
        self.set_image()
        self.set_commonscat()
        self.set_coords(("lat", "lon"))
        self.set_inception()
        # self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("ca", "fr", CaFr)
    dataset.data_files = {"provinces": "canada_provinces_fr.json"}
    dataset.lookup_downloads = {}
    importer.main(args, dataset)
