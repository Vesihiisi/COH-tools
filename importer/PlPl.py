from Monument import Monument
import importer_utils as utils


class PlPl(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.nazwa)
        self.add_label("pl", name)

    def set_adm_location(self):
        """
        TODO
        These are not wikilinked...
        And the labels on wd are in different formats,
        sometimes with 'gmina' and sometimes without.
        How to match them correctly?
        """
        if "gmina " in self.gmina:
            municipality = self.gmina.split(" ")[1:]
            municipality = ' '.join(municipality)
        else:
            municipality = self.gmina

    def set_no(self):
        """
        TODo
        Examples of what these can look like: http://tinyurl.com/jz5vuc4
        isolate the date and use as start_time
        sometimes there are two values:
        250 z 16.08.1957, 8 z 17.02.1981 (WUOZ - A/463)
        first step: split on comma OR semicolon?
        or start by isolating the dates and work backwards
        """
        # print(self.numer)
        return

    def set_address(self):
        """
        NOTE
        Sometimes this is broken and only a number is included,
        like "70".
        But then you can't just test for if it's only number
        because sometimes it's like "70 B"
        Check for length? Min 5 characters?
        """
        if self.has_non_empty_attribute("adres") and len(self.adres) > 5:
            street = utils.remove_markup(self.adres)
            self.add_statement("located_street", street)

    def set_location(self):
        settlements_dict = self.data_files["settlements"]
        if utils.count_wikilinks(self.miejscowosc) == 1:
            location = utils.q_from_first_wikilink("pl", self.miejscowosc)
            self.add_statement("location", location)
        else:
            placename = remove_markup(self.miejscowosc)
            try:
                location = [x["item"] for x in settlements_dict if x[
                    "pl"].strip() == placename][0]
                self.add_statement("location", location)
            except IndexError:
                return

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("pl")
        self.set_commonscat()
        self.set_image("zdjecie")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_no()
        self.set_location()
        # self.set_sagsnr()
        self.set_address()
        # self.set_inception()
        self.exists_with_prop(mapping)
        # self.print_wd()
