from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class DkFortidsDa(Monument):

    def update_labels(self):
        """Set Danish label of the object."""
        self.add_label("da", utils.remove_markup(self.stednavn))

    def update_descriptions(self):
        """
        Set descriptions of the object.

        All the objects have a "type" field.
        Use it in connection with the municipality:
        "skanse i Nyborg Kommune"
        """
        mun_dict = self.data_files["municipalities"]
        monument_type = utils.remove_markup(self.type).lower()
        municipality_da = utils.remove_markup(self.kommune)
        description_da = "{} i {}".format(monument_type, municipality_da)
        self.add_description("da", description_da)

        try:
            location_en = [x["en"]
                           for x in mun_dict if x["da"] == municipality_da]
            location_en = location_en[0]
        except IndexError:
            location_en = "Denmark"
        description_en = "ancient monument in {}".format(location_en)

        try:
            location_sv = [x["sv"]
                           for x in mun_dict if x["da"] == municipality_da]
            location_sv = location_sv[0]
        except IndexError:
            location_sv = "Danmark"
        description_sv = "fornlämning i {}".format(location_sv)

        self.add_description("en", description_en)
        self.add_description("sv", description_sv)

    def set_adm_location(self):
        """
        Set municipality of the object.

        Note: All distinct values in this column are wikilinked
        and in the form "[[Allerød Kommune]]".
        For safety, compare with offline list of Danish municipalities.
        """
        mun_dict = self.data_files["municipalities"]
        if self.has_non_empty_attribute("kommune"):
            if utils.count_wikilinks(self.kommune) == 1:
                try:
                    adm_q = utils.q_from_first_wikilink(
                        "da", self.kommune)
                    municipality = [x["item"] for
                                    x in mun_dict if x["item"] == adm_q]
                    municipality = municipality[0]
                    self.add_statement("located_adm", municipality)
                except IndexError:
                    self.add_to_report("kommune", self.kommune)

    def set_type(self):
        """
        Set specific type of the object.

        https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/dk-fortidsminder_(da)/types
        If parsed successfully, substitute the default "ancient monument".
        """
        if self.has_non_empty_attribute("type"):
            table = self.data_files["types"]["mappings"]
            try:
                special_type = [table[x]["items"]
                                for x in table
                                if x == self.type]
                special_type = special_type[0][0]
                self.substitute_statement("is", special_type)
            except IndexError:
                self.add_to_report("type", self.type)

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.systemnummer)

    def set_id(self):
        """Set ancient monument ID (P3596)."""
        danish_id = str(self.systemnummer)
        self.add_statement("danish_ancient_monument_id", danish_id)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("da", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_heritage()
        self.set_country()
        self.set_source()
        self.set_registrant_url()
        self.set_is()
        self.update_labels()
        self.update_descriptions()
        self.set_commonscat()
        self.set_image("billede")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_type()
        self.set_id()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("dk-fortidsminder", "da", DkFortidsDa)
    dataset.data_files = {
        "types": "dk-fortidsminder_(da)_types.json",
        "municipalities": "denmark_municipalities.json"}
    importer.main(args, dataset)
