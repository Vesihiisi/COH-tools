from Monument import Monument
import importer_utils as utils


class ByBeTarask(Monument):

    def set_location(self):
        if self.has_non_empty_attribute("place"):
            place_item = utils.q_from_first_wikilink("be-tarask", self.place.title())
            place_item_ids = utils.get_P31(place_item, self.repo)
            for p31_value in place_item_ids:
                if p31_value in self.data_files["settlement"]:
                    self.add_statement("location", place_item)
                    # there can be more than one P31, but after first positive
                    # we can leave
                    return

    def update_labels(self):
        name = utils.remove_markup(self.name)
        self.add_label("be-tarask", name)

    def set_heritage_id(self):
        self.add_statement("belarus_monument_id", self.id)

    def update_heritage(self):
        herit_cats = {
            "1": "Q28464210",
            "2": "Q28464212",
            "3": "Q28464213",
            "0": "Q28464209"
        }
        if self.has_non_empty_attribute("category"):
            herit_spec = herit_cats[self.category]
            self.substitute_statement("heritage_status", herit_spec)

    def set_monuments_all_id(self):
        self.monuments_all_id = self.id

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("be-tarask", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_is()
        self.set_coords(("lat", "lon"))
        self.set_heritage_id()
        self.set_heritage()
        self.update_heritage()
        self.update_labels()
        self.set_image()
        self.set_commonscat()
        self.set_location()
        self.set_wd_item(self.find_matching_wikidata(mapping))
