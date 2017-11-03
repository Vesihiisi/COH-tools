from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class ClEs(Monument):

    def update_labels(self):
        self.add_label("es", utils.get_rid_of_brackets(self.monumento))

    def update_descriptions(self):
        descs = {
            "es": "Monumento Nacional de Chile",
            "en": "national monument of Chile"}
        for lang in descs:
            self.add_description(lang, descs[lang])

    def update_heritage(self):
        heritages = {"MH": "Q35863415", "ZT": "Q6171610"}
        if self.tipo in heritages.keys():
            self.remove_statement("heritage_status")
            protection_date = utils.parse_date_spanish(self.fecha)
            date_dict = utils.date_to_dict(protection_date, "%d-%m-%Y")
            start_time = {"start_time": {"time_value": date_dict}}
            self.add_statement("heritage_status",
                               heritages[self.tipo], start_time)

    def set_directions(self):
        if self.has_non_empty_attribute("direccion"):
            monolingual = utils.package_monolingual(
                utils.remove_markup(self.direccion), 'es')
            self.add_statement("directions", monolingual)

    def set_adm_location(self):
        adm_location_q = False
        municip_dict = self.data_files["municipalities"]
        region_dict = self.data_files["regions"]
        if utils.count_wikilinks(self.comuna) == 1:
            comuna_q = (utils.q_from_first_wikilink("es", self.comuna))
            comuna_match = [x for x in municip_dict if x["item"] == comuna_q]
            if len(comuna_match) == 1:
                adm_location_q = comuna_q
            else:
                region_iso_match = [x["item"]
                                    for x in region_dict
                                    if x["iso_code"] == self.ISO]
                if len(region_iso_match) == 1:
                    adm_location_q = region_iso_match[0]
        if adm_location_q:
            self.add_statement("located_adm", adm_location_q)
        else:
            self.add_to_report("comuna", self.comuna, "located_adm")

    def set_heritage_id(self):
        wlm_code = self.mapping["table_name"].upper()
        heritage = "{}-{}".format(wlm_code, self.id)
        self.add_statement("wlm_id", heritage)

    def exists_with_monument_article(self, language):
        return self.get_multi_param_monument_article(
            raw="monumento_enlace",
            linked="monumento",
            blocks="enlace",
            language=language)

    def set_parts(self):
        if self.has_non_empty_attribute("enlace"):
            parts_raw = self.enlace
            parts_links = utils.get_wikilinks(parts_raw)
            for link in parts_links:
                part_q = utils.q_from_wikipedia("es", link.title)
                if part_q:
                    self.add_statement("has_part", part_q)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        if self.tipo == "SN":
            self.upload = False
            return

        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage()
        self.update_heritage()
        self.set_country()
        self.set_adm_location()
        self.set_directions()
        self.set_heritage_id()
        self.set_is()
        self.set_parts()
        self.set_commonscat()
        self.set_coords()
        self.set_image("imagen")
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("cl", "es", ClEs)
    dataset.data_files = {
        "municipalities": "chile_municipalities.json",
        "regions": "chile_regions.json"
    }
    importer.main(args, dataset)
