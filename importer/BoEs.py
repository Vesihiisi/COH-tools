from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class BoEs(Monument):

    def set_adm_location(self):
        """
        Set the administrative location.

        First try to resolve the municipality,
        and if that doesn't work use the department
        which is a higher unit.
        """
        match = None
        if self.has_non_empty_attribute("municipio"):
            try_match = utils.q_from_first_wikilink("es", self.municipio)
            link_match = utils.get_item_from_dict_by_key(
                dict_name=self.data_files["admin"],
                search_term=try_match,
                search_in="item")
            if len(link_match) == 1:
                match = link_match[0]
            else:
                self.add_to_report("municipio", self.municipio, "located_adm")
        if not match:
            dep_match = utils.get_item_from_dict_by_key(
                dict_name=self.data_files["departments"],
                search_term=self.iso,
                search_in="iso")
            if len(dep_match) == 1:
                match = dep_match[0]
            else:
                self.add_to_report("iso", self.iso, "located_adm")

        if match:
            self.add_statement("located_adm", match)

    def update_labels(self):
        spanish = utils.remove_markup(self.monumento)
        self.add_label("es", spanish)

    def set_heritage_id(self):
        """Set the WLM ID as heritage ID with a CO-prefix."""
        wlm = "{}-{}".format(self.mapping["table_name"].upper(), self.id)
        self.add_statement("wlm_id", wlm)
        self.add_disambiguator(str(self.id))

    def set_directions(self):
        if self.has_non_empty_attribute("direccion"):
            monolingual = utils.package_monolingual(
                utils.remove_markup(self.direccion), 'es')
            self.add_statement("directions", monolingual)

    def exists_with_monument_article(self, language):
        return self.get_multi_param_monument_article(
            raw="monumento_enlace",
            linked="monumento",
            blocks="enlace",
            language=language)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_adm_location()
        self.set_directions()
        self.set_is()
        self.set_heritage()
        self.set_commonscat()
        self.set_image()
        self.set_heritage_id()
        self.set_coords()
        self.update_labels()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("bo", "es", BoEs)
    dataset.data_files = {
        "admin": "bolivia_admin.json",  # http://tinyurl.com/y7ffsgou
        "departments": "bolivia_department.json"  # http://tinyurl.com/y9oenz78
    }
    importer.main(args, dataset)
