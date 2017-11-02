from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class UaUk(Monument):

    def set_image(self):
        """
        Special set image case.

        Ignore if image is template saying there
        will be no image because of freedom of panorama
        issues.
        """
        if self.has_non_empty_attribute("image"):
            if self.image == '{{неволя}}':
                super().set_image

    def set_adm_location(self):
        """
        Set administrative location.

        'municipality' contains both wlinked
        and clean values. If clean, try to match from
        external file -- it's a mix of various types of
        things (raion, municip etc), so the file is quite large...

        If no match from municipality, resort to
        oblast match via iso.
        """
        adm_match = None
        adm_dict = self.data_files["administrative"]
        obl_dict = self.data_files["oblasti"]

        if self.has_non_empty_attribute("municipality"):
            if len(utils.get_wikilinks(self.municipality)) == 1:
                adm_match = utils.q_from_first_wikilink("uk",
                                                        self.municipality)

        if not adm_match:
            adm_try = utils.get_item_from_dict_by_key(dict_name=adm_dict,
                                                      search_term=self.municipality,
                                                      search_in="itemLabel")
            if len(adm_try) == 1:
                adm_match = adm_try[0]

        if not adm_match:
            iso = self.iso_oblast
            adm_try = utils.get_item_from_dict_by_key(dict_name=obl_dict,
                                                      search_in="iso",
                                                      search_term=iso)
            if len(adm_try) == 1:
                adm_match = adm_try[0]

        self.add_statement("located_adm", adm_match)

    def set_directions(self):
        if self.has_non_empty_attribute("address"):
            dirs = utils.remove_markup(self.address)
            monoling = utils.package_monolingual(dirs, 'uk')
            self.add_statement("directions", monoling)

    def update_labels(self):
        uk = utils.remove_markup(self.name)
        self.add_label("uk", uk)

    def set_heritage_id(self):
        wlm = "{}-{}".format(self.mapping["table_name"].upper(), self.id)
        self.add_statement("wlm_id", wlm)
        self.add_disambiguator(str(self.id))

    def update_descriptions(self):
        descs = {
            "ru": "объект культурного наследия Украины",
            "uk": "пам'ятка культурної спадщини України",
            "en": "cultural heritage site in Ukraine"
        }
        for lang in descs:
            self.add_description(lang, descs[lang])

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_coords()
        self.set_is()
        self.set_country()
        self.set_adm_location()
        self.set_directions()
        self.set_heritage()
        self.set_heritage_id()
        self.set_image()
        self.set_commonscat()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("ua", "uk", UaUk)
    dataset.data_files = {
        "oblasti": "ukraine_oblasti.json",
        "administrative": "ukraine_admin.json"  # http://tinyurl.com/y7rzg6wt
    }
    importer.main(args, dataset)
