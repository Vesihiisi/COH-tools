from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class DkBygningDa(Monument):

    def set_adm_location(self):
        if self.has_non_empty_attribute("kommune"):
            if utils.count_wikilinks(self.kommune) == 1:
                adm_location = utils.q_from_first_wikilink("da", self.kommune)
                self.add_statement("located_adm", adm_location)

    def set_location(self):
        """
        Set location based on 'by' column.

        If there's one wikilinked item, confirm that
        the corresponding WD item is of a type that's
        a subclass of 'human settlement', using query results
        downloaded by importer.
        If not wikilinked, check if there's a dawp article
        with the same name and do the same check.
        """
        place_item = None
        if self.has_non_empty_attribute("by"):
            place = self.by
            if utils.count_wikilinks(place) == 1:
                place = utils.get_wikilinks(place)[0].title
            if utils.wp_page_exists("da", place):
                place_item = utils.q_from_wikipedia("da", place)
        if place_item:
            place_item_ids = utils.get_P31(place_item, self.repo)
            for p31_value in place_item_ids:
                if p31_value in self.data_files["settlement"]:
                    self.add_statement("location", place_item)
                    # there can be more than one P31, but after first positive
                    # we can leave
                    return

    def set_sagsnr(self):
        """Danish listed buildings case ID (P2783)."""
        self.add_statement("listed_building_dk", str(self.sagsnr))

    def update_labels(self):
        self.add_label("da", utils.remove_markup(self.sagsnavn))

    def set_address(self):
        """
        Set address of object.

        self.addresse is always streetname + number.
        self.postnr is always zipcode
        self.by is always placename.
        """
        if self.has_non_empty_attribute("adresse"):
            address = self.adresse + " " + self.postnr + " " + self.by
            self.add_statement("located_street", address)

    def set_inception(self):
        if self.has_non_empty_attribute("opforelsesar"):
            inception = utils.parse_year(self.opforelsesar)
            if isinstance(inception, int):
                self.add_statement(
                    "inception", utils.package_time({"year": inception}))

    def set_monuments_all_id(self):
        """Map monuments_all ID to fields in this table."""
        self.monuments_all_id = "{!s}-{!s}-{!s}".format(
            self.kommunenr, self.ejendomsnr, self.bygningsnr)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.set_monuments_all_id()
        self.update_labels()
        self.exists("da")
        self.set_commonscat()
        self.set_image("billede")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_location()
        self.set_sagsnr()
        self.set_address()
        self.set_inception()
        self.exists_with_prop(mapping)
        self.print_wd()


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("dk-bygninger", "da", DkBygningDa)
    dataset.subclass_downloads = {"settlement": "Q486972"}
    importer.main(args, dataset)
