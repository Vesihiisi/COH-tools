from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class MtDe(Monument):

    def set_adm_location(self):
        """
        Set the administrative location.

        Use the 'gemeinde' field to resolve
        municipality via wp link first, then if unable,
        region-iso code via mapping.
        """
        adm_q = None
        municip_raw = self.gemeinde
        adm_q = utils.q_from_wikipedia("de", municip_raw)
        if adm_q is None:
            adm_iso_match = [x for x in self.data_files[
                "regions"] if x["iso"] == self.region_iso]
            if len(adm_iso_match) == 1:
                adm_q = adm_iso_match[0]["item"]

        if adm_q:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report("gemeinde", self.gemeinde, "located_adm")

    def update_labels(self):
        labels = {
            "de": self.name_de,
            "en": self.name_en,
            "mt": self.name_mt
        }
        for lang, label in labels.items():
            self.add_label(lang, label)

    def update_descriptions(self):
        """
        Set the descriptions in en and mt.

        Try to add the place name. Since the municipality
        names are titles of articles, sometimes they
        have the form of "$municipality (Malta)", in which
        case remove the bracketed part.
        """
        patterns = {
            "en": "cultural property in {}",
            "mt": "propjeta' kulturali ġewwa {}"
        }
        placename = "Malta"
        for lg, descr in patterns.items():
            if self.has_non_empty_attribute("gemeinde"):
                municip_base = utils.get_rid_of_brackets(self.gemeinde)
                placename = "{}, {}".format(municip_base, "Malta")
                self.add_description(lg, descr.format(placename))

    def set_monuments_all_id(self):
        self.monuments_all_id = self.inventarnummer

    def set_heritage_id(self):
        id_no = self.inventarnummer.zfill(5)
        qual_url = {"described_at_url": self.registrant_url}
        self.add_statement("malta_monument_id", id_no, qual_url)

    def set_street_address(self):
        """
        Set the street address.

        These all have nice looking street addresses, which, however,
        do not include the municipality name.
        So add it to the address after stripping potential
        bracketed part.
        """
        if utils.contains_digit(self.adresse):
            city_clean = utils.get_rid_of_brackets(self.gemeinde)
            address = "{}, {}".format(self.adresse, city_clean)
            self.add_statement("located_street", address)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("de", "artikel")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_registrant_url()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_heritage_id()
        self.set_image("foto")
        self.set_commonscat()
        self.set_coords(("lat", "lon"))
        self.set_is()
        self.set_heritage()
        self.update_labels()
        self.update_descriptions()
        self.set_adm_location()
        self.set_street_address()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("mt", "de", MtDe)
    dataset.data_files = {"councils": "malta_councils.json"}
    dataset.lookup_downloads = {}
    importer.main(args, dataset)
