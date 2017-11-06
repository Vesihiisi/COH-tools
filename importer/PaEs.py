from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class PaEs(Monument):

    def set_adm_location(self):
        """Set the Admin Location, using iso code of Province."""
        self.set_from_dict_match(
            lookup_dict=self.data_files["provinces"],
            dict_label="iso",
            value_label="prov_iso",
            prop="located_adm"
        )

    def set_directions(self):
        if self.has_non_empty_attribute("direccion"):
            monolingual = utils.package_monolingual(
                utils.remove_markup(self.direccion), 'es')
            self.add_statement("directions", monolingual)

    def update_labels(self):
        self.add_label("es", utils.remove_markup(self.nombre))

    def update_descriptions(self):
        english = "cultural monument of Panama"
        self.add_description("en", english)

    def set_heritage_id(self):
        wlm_code = self.mapping["table_name"].upper()
        heritage = "{}-{}".format(wlm_code, self.id)
        self.add_statement("wlm_id", heritage)

    def set_commonscat(self):
        """
        Set the Commons cat property.

        There's a number of 'weird' values like
        'Cultural heritage monuments in $province'
        so detect those and fall back on monumento_categoria
        in this case
        """
        if not self.commonscat.startswith("Cultural heritage monuments"):
            super().set_commonscat()
        elif self.has_non_empty_attribute("monumento_categoria"):
            super().set_commonscat("monumento_categoria")

    def exists_with_monument_article(self, language):
        """
        Set article about the object.

        Note that "articulo" goes to the "main article", often one level above
        the particular object.
        """
        if self.has_non_empty_attribute("nombre"):
            return utils.q_from_first_wikilink("es", self.nombre)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage()
        self.set_country()
        self.set_adm_location()
        self.set_directions()
        self.set_heritage_id()
        self.set_is()
        self.set_commonscat()
        self.set_coords()
        self.set_image("imagen")
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("pa", "es", PaEs)
    dataset.data_files = {"provinces": "panama_provinces.json"}
    importer.main(args, dataset)
