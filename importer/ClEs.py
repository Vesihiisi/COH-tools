from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer
import dateparser


class ClEs(Monument):

    def update_labels(self):
        spanish = utils.get_rid_of_brackets(
            utils.remove_markup(self.monumento))
        self.add_label("es", spanish)

    def update_descriptions(self):
        descs = {
            "es": "Monumento Nacional de Chile",
            "en": "national monument of Chile"}
        for lang in descs:
            self.add_description(lang, descs[lang])

    def set_heritage(self):
        """
        Set heritage status with optional qualifiers.

        The heritage type is set by 'tipo'
        Use 'decreto' as 'legal_citation'.
        Extract date from 'fecha' as 'start time'.
        """
        quals = {}

        heritage_default = self.mapping["heritage"]["item"]
        heritages = {
            "MH": "Q35863415",
            "SN": "Q35863088",
            "ZT": "Q6171610"
        }
        heritage_item = heritages.get(self.tipo) or heritage_default

        if self.has_non_empty_attribute("decreto"):
            quals["legal_citation"] = self.decreto

        if self.has_non_empty_attribute("fecha"):
            es_date = dateparser.parse(self.fecha, languages=['es'])
            if es_date:
                date_dict = utils.datetime_object_to_dict(es_date)
                quals["start_time"] = utils.package_time(date_dict)
            else:
                self.add_to_report("fecha", self.fecha, "start_time")

        self.add_statement("heritage_status", heritage_item, quals)

    def set_directions(self):
        if self.has_non_empty_attribute("direccion"):
            monolingual = utils.package_monolingual(
                utils.remove_markup(self.direccion), 'es')
            self.add_statement("directions", monolingual)

    def set_adm_location(self):
        """
        Set the Admin Location.

        Use the linked Municipality first, checking
        against external list.
        If failed, use the Region iso code, which is a
        bigger unit.
        """
        adm_q = None
        municip_dic = self.data_files["municipalities"]
        region_dict = self.data_files["regions"]

        municip_q = utils.q_from_first_wikilink("es", self.comuna)
        if utils.get_item_from_dict_by_key(dict_name=municip_dic,
                                           search_term=municip_q,
                                           search_in="item"):
            adm_q = municip_q
        else:
            self.add_to_report("comuna", self.comuna, "located_adm")

        if adm_q is None:
            iso_match = utils.get_item_from_dict_by_key(
                dict_name=region_dict,
                search_term=self.ISO,
                search_in="iso")
            if len(iso_match) == 1:
                adm_q = iso_match[0]
            else:
                self.add_to_report("ISO", self.ISO, "located_adm")

        if adm_q:
            self.add_statement("located_adm", adm_q)

    def set_heritage_id(self):
        wlm_code = self.mapping["table_name"].upper()
        heritage = "{}-{}".format(wlm_code, self.id)
        self.add_statement("wlm_id", heritage)
        self.add_disambiguator(str(self.id))

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
                else:
                    self.add_to_report("enlace", self.enlace, "has_part")

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
