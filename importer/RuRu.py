from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class RuRu(Monument):

    def set_adm_location(self):
        """
        Set the administrative location.

        Preferably try to resolve the 'district' (район/округ,
        the field contains different types so that's why we're
        matching it against the whole big list of administrative
        divisions of different kinds).
        If that doesn't work, use the higher level субъект.
        """
        level_three = self.data_files["administrative"]
        level_two = self.data_files["subyekty"]
        district_match = [x for x in level_three if x[
            "itemLabel"] == self.district]
        if len(district_match) == 1:
            self.add_statement("located_adm", district_match[0]["item"])
        else:
            sub_match = [x for x in level_two if x[
                "value"].lower() == self.region_iso]
            if len(sub_match) == 1:
                self.add_statement("located_adm", sub_match[0]["item"])
            else:
                self.add_to_report("district", self.district, "located_adm")

    def set_location(self):
        """
        Set the location property using 'city' field.

        Of course it's often a village etc. :)
        Make sure that the target page has a P31 of a
        settlement, to avoid disambigs etc.
        Also, compare with 'administrative location' of the
        object, and don't add if it's the same.
        """
        if self.has_non_empty_attribute("city"):
            city_q_try = utils.q_from_wikipedia("ru", self.city)
            try:
                administrative_q = self.wd_item[
                    "statements"]["P131"][0]["value"]
            except KeyError:
                administrative_q = None
            if city_q_try and city_q_try != administrative_q:
                city_q_is = utils.get_P31(city_q_try, self.repo)
                for p31_value in city_q_is:
                    if p31_value in self.data_files["settlement"]:
                        self.add_statement("location", city_q_try)
                        # there can be more than one P31,
                        # but after first positive
                        # we can leave
                        return
                    else:
                        self.add_to_report("city", self.city, "location")

    def update_labels(self):
        self.add_label("ru", self.name)

    def update_descriptions(self):
        desc = "cultural heritage site in Russia"
        self.add_description("en", desc)

    def set_heritage_id(self):
        self.add_statement("kulturnoe-nasledie", self.id)

    def set_monuments_all_id(self):
        self.monuments_all_id = self.id

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("ru", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_adm_location()
        self.set_location()
        self.set_is()
        self.set_heritage()
        self.set_image()
        self.set_commonscat()
        self.set_heritage_id()
        self.set_coords(("lat", "lon"))
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("ru", "ru", RuRu)
    dataset.data_files = {
        "administrative": "russia_administrative.json",
        "subyekty": "russia_subyekty.json"
    }
    dataset.lookup_downloads = {}
    dataset.subclass_downloads = {"settlement": "Q486972"}
    importer.main(args, dataset)
