from Monument import Monument
import importer_utils as utils


class SeShipSv(Monument):

    """
    TODO
    * handle material (from lookup table)
    """

    def set_type(self):
        table = self.data_files["functions"]["mappings"]
        if self.funktion:
            special_type = self.funktion.lower()
            try:
                functions = [table[x]["items"]
                             for x in table if x.lower() == special_type][0]
                if len(functions) > 0:
                    self.remove_statement("is")
                    for f in functions:
                        self.add_statement("is", f)
            except IndexError:
                return

    def set_shipyard(self):
        if self.has_non_empty_attribute("varv"):
            possible_varv = self.varv
            if "<br>" in possible_varv:
                possible_varv = self.varv.split("<br>")[0]
            if "[[" in possible_varv:
                varv = utils.q_from_first_wikilink("sv", possible_varv)
                self.add_statement("manufacturer", varv)

    def set_manufacture_year(self):
        """
        TODO
        !!!!!
        add "year" etc. so that it can be processed by pywikibot
        See:
        """
        if self.has_non_empty_attribute("byggar"):
            byggar = utils.parse_year(
                utils.remove_characters(self.byggar, ".,"))
            self.add_statement("inception", {"time_value": byggar})

    def set_dimensions(self):
        if self.has_non_empty_attribute("dimensioner"):
            dimensions_processed = utils.parse_ship_dimensions(
                self.dimensioner)
            for dimension in dimensions_processed:
                if dimension in self.props:
                    value = dimensions_processed[dimension]
                    self.add_statement(
                        dimension, {"quantity_value": value,
                                    "unit": self.props["metre"]})

    def set_homeport(self):
        if self.has_non_empty_attribute("hemmahamn"):
            if utils.count_wikilinks(self.hemmahamn) == 1:
                home_port = utils.q_from_first_wikilink("sv", self.hemmahamn)
                self.add_statement("home_port", home_port)

    def set_call_sign(self):
        if self.has_non_empty_attribute("signal"):
            self.add_statement("call_sign", self.signal)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.set_labels("sv", self.namn)
        self.set_image("bild")
        self.exists("sv", "artikel")
        self.set_type()
        self.set_commonscat()
        self.set_call_sign()
        self.set_manufacture_year()
        self.set_shipyard()
        self.set_homeport()
        self.set_dimensions()
        self.exists_with_prop(mapping)
