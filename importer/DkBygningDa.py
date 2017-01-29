from Monument import Monument
import importer_utils as utils


class DkBygningDa(Monument):

    def set_adm_location(self):
        if self.has_non_empty_attribute("kommune"):
            if utils.count_wikilinks(self.kommune) == 1:
                adm_location = utils.q_from_first_wikilink("da", self.kommune)
                self.add_statement("located_adm", adm_location)

    def set_location(self):
        """
        Use self.municipality because IT'S PLACE NOT MUNICIPALITY
        (that's adm2)
        """
        place_item = False
        if self.has_non_empty_attribute("by"):
            place = self.by
            if utils.count_wikilinks(place) == 1:
                place_item = utils.q_from_first_wikilink("da", place)
            else:
                if utils.wp_page_exists("da", place):
                    place_item = utils.q_from_wikipedia("da", place)
        if place_item:
            self.add_statement("location", place_item)

    def set_sagsnr(self):
        """
        Danish listed buildings case ID (P2783)
        """
        self.add_statement("listed_building_dk", str(self.sagsnr))

    def update_labels(self):
        self.add_label("da", utils.remove_markup(self.sagsnavn))

    def set_address(self):
        """
        Really nice addresses in this table.
        """
        if self.has_non_empty_attribute("adresse"):
            address = self.adresse + " " + self.postnr + " " + self.by
            self.add_statement("located_street", address)

    def set_inception(self):
        if self.has_non_empty_attribute("opforelsesar"):
            inception = utils.parse_year(self.opforelsesar)
            self.add_statement("inception", {"time_value": inception})

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
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
        # self.print_wd()


