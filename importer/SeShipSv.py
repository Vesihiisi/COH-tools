from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class SeShipSv(Monument):

    def set_type(self):
        """
        Set the specific type of watercraft.

        In some cases, there's a more specific ship type in
        the 'funktion' column.
        Here all all the possible values:
        https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/se-ship_(sv)/functions
        This table is used as the base for mapping.
        If there's a mapping for the specific value,
        it will substitute the default P31 (watercraft)
        """
        table = self.data_files["functions"]["mappings"]
        if self.funktion:
            special_type = self.funktion.lower()
            try:
                functions = [table[x]["items"]
                             for x in table if x.lower() == special_type][0]
                if len(functions) > 0:
                    self.remove_statement("is")
                    for f in functions:
                        ref = self.wlm_source
                        self.add_statement("is", f, refs=[ref])
            except IndexError:
                self.add_to_report("funktion", self.funktion)

    def set_shipyard(self):
        """
        Set the manufacturer property.

        Process the column 'varv'.
        It can look like this:
        '[[Bergsunds varv]]<br>[[Stockholm]]'
        We only use this if the actual shipyard is
        wikilinked, which is not always the case.
        Use WLM database as reference.
        """
        if self.has_non_empty_attribute("varv"):
            possible_varv = self.varv
            if "<br>" in possible_varv:
                possible_varv = self.varv.split("<br>")[0]
            if "[[" in possible_varv:
                varv = utils.q_from_first_wikilink("sv", possible_varv)
                ref = self.wlm_source
                self.add_statement("manufacturer", varv, refs=[ref])
            else:
                self.add_to_report("varv", self.varv)

    def set_manufacture_year(self):
        """
        Set the manufacture year.

        If the column 'byggar' has a parsable value,
        use it as year of manufacture.
        Use WLM database as a source.
        """
        if self.has_non_empty_attribute("byggar"):
            byggar = utils.parse_year(
                utils.remove_characters(self.byggar, ".,"))
            if isinstance(byggar, int):
                ref = self.wlm_source
                self.add_statement(
                    "inception", utils.package_time({"year": byggar}),
                    refs=[ref])
            else:
                self.add_to_report("byggår", self.byggar)

    def set_dimensions(self):
        """
        Parse ship dimensions.

        They can look like this:
        'Längd: 15.77 Bredd: 5.19 Djup: 1.70 Brt: 15'
        If parsing fails, set it to an empty dictionary
        and save the input data to the problem report.
        Use WLM database as source.
        """
        if self.has_non_empty_attribute("dimensioner"):
            dimensions_processed = utils.parse_ship_dimensions(
                self.dimensioner)
            if not dimensions_processed:
                self.add_to_report("dimensioner", self.dimensioner)
            else:
                for dimension, value in dimensions_processed.items():
                    if dimension in self.props:
                        ref = self.wlm_source
                        self.add_statement(
                            dimension,
                            utils.package_quantity(
                                value, self.common_items["metre"]),
                            refs=[ref])

    def set_homeport(self):
        """
        Add homeport to data object.

        Only works if column 'hemmahamn' contains exactly
        one wikilink.
        Use WLM database as source.
        """
        if self.has_non_empty_attribute("hemmahamn"):
            if utils.count_wikilinks(self.hemmahamn) == 1:
                home_port = utils.q_from_first_wikilink("sv", self.hemmahamn)
                ref = self.wlm_source
                self.add_statement("home_port", home_port, refs=[ref])

    def set_call_sign(self):
        """
        Add call sign to data object.

        [https://phabricator.wikimedia.org/T159427]
        A few of them are fake
        (since identifiers are needed in the WLM database).
        These have the shape wiki[0-9][0-9].
        Fake ID's are added as P2186 (WLM identifier).
        All values: https://phabricator.wikimedia.org/P5010

        Use WLM database as source.
        """
        if self.has_non_empty_attribute("signal"):
            ref = self.wlm_source
            if self.signal.startswith("wiki") or self.signal.startswith("Tidigare"):
                self.add_statement("wlm_id", self.signal, refs=[ref])
            else:
                self.add_statement("call_sign", self.signal, refs=[ref])

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = self.signal

    def set_descriptions(self):
        """Set default descriptions."""
        desc_bases = {"sv": "kulturmärkt bruksfartyg",
                      "en": "listed historical ship in Sweden"}
        for language in ["en", "sv"]:
            self.add_description(language, desc_bases[language])

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_is()
        self.set_heritage()
        self.set_source()
        self.set_registrant_url()
        self.set_labels("sv", self.namn)
        self.set_descriptions()
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


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("se-ship", "sv", SeShipSv)
    dataset.data_files = {
        "functions": "se-ship_(sv)_functions.json"}
    importer.main(args, dataset)
