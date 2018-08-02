from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class SeArbetslSv(Monument):

    def set_descriptions(self):
        """Set default descriptions."""
        DESC_BASES = {"sv": "arbetslivsmuseum",
                      "en": "working life museum",
                      "fi": "työväen museo Ruotsissa",
                      "ru": "музей в Швеции",
                      "pl": "muzeum w Szwecji"}
        for language in ["en", "sv", "fi", "ru", "pl"]:
            self.add_description(language, DESC_BASES[language])

    def add_location_to_desc(self, language, municipality):
        """Append municipality name to description."""
        if language == "sv":
            self.wd_item["descriptions"][language] += " i " + municipality
        elif language == "en":
            self.wd_item["descriptions"][
                language] += " in " + municipality + ", Sweden"

    def set_adm_location(self):
        """
        Set the administrative location.

        Use offline mapping file
        to map municipality to P131.
        The column is 'kommun'.
        It looks like this:
            Alingsås
        Just the name of the municipality
        without the word kommun or genitive.
        THEN use the administrative location in description
        in both English and Swedish.

        If raw data cannot be matched, add to problem report.
        """
        municip_dict = self.data_files["municipalities"]
        if self.kommun == "Göteborg":
            municip_name = "Gothenburg"
        else:
            municip_name = self.kommun
        pattern = municip_name.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "en"].lower() == pattern][0]
            self.add_statement("located_adm", municipality)
            swedish_name = [x["sv"]
                            for x in municip_dict
                            if x["item"] == municipality][0]
            english_name = [x["en"]
                            for x in municip_dict
                            if x["item"] == municipality][0]
            self.add_location_to_desc("sv", swedish_name)
            self.add_location_to_desc("en", english_name)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.kommun))
            self.add_to_report("kommun", self.kommun)
            return

    def set_type(self):
        """
        Add specific type of museum.

        Use the lookup table from:
        https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/se-arbetsl_(sv)/types
        If there's a specific type, it will be added to the default
        "working life museum", resulting in two P31's for this item.

        If raw data cannot be matched, add to problem report.
        """
        if self.has_non_empty_attribute("typ"):
            table = self.data_files["types"]["mappings"]
            type_to_search_for = self.typ.lower()
            try:
                special_type = [table[x]["items"]
                                for x in table
                                if x.lower() == type_to_search_for][0]
                for special in special_type:
                    self.add_statement("is", special)
            except IndexError:
                self.add_to_report("typ", self.typ)
        return

    def set_location(self):
        """
        Set the location.

        Using external file of all populated places in Sweden,
        and the 'ort' column,
        add location statement.
        The file contains all subclasses of settlement,
        such as town, village, etc.

        If raw data cannot be matched, add to problem report.
        """
        settlements_dict = self.data_files["settlements"]
        if self.has_non_empty_attribute("ort"):
            try:
                location = [x["item"] for x in settlements_dict if x[
                    "sv"].strip() == utils.remove_markup(self.ort)][0]
                self.add_statement("location", location)
            except IndexError:
                self.add_to_report("ort", self.ort)

    def set_id(self):
        """Add ID number from ARBETSAM database."""
        if self.has_non_empty_attribute("id"):
            ref = self.arbetsam_source
            self.add_statement("arbetsam", self.id, refs=ref)

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = self.id

    def set_is(self):
        """
        Set P31 of all items.

        They're all a working life museum,
        even if they can be something else in addition.
        """
        arbetslivsmuseum = "Q10416961"
        ref = self.arbetsam_source
        self.add_statement("is", arbetslivsmuseum, refs=ref)

    def exists_with_monument_article(self, language):
        """Set language of Wikipedia to use to match articles."""
        return super().exists_with_monument_article("sv")

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.arbetsam_source = self.create_stated_in_source(
            "Q28834837", "2013-11-28")
        self.set_id()
        self.set_country()
        self.set_source()
        self.set_registrant_url()
        self.set_is()
        self.set_labels("sv", self.namn)
        self.set_descriptions()
        self.set_type()
        self.set_adm_location()
        self.set_location()
        self.set_street_address("sv", "adress")
        self.set_image("bild")
        self.set_commonscat()
        self.set_coords(("lat", "lon"))
        self.set_wd_item(self.find_matching_wikidata(mapping))
        # self.print_wd()


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("se-arbetsl", "sv", SeArbetslSv)
    dataset.data_files = {
        "municipalities": "sweden_municipalities.json",
        "types": "se-arbetsl_(sv)_types.json",
        "settlements": "sweden_settlements.json"}
    importer.main(args, dataset)
