from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer
import dateparser


class EsEs(Monument):

    def set_heritage_with_date(self):
        """
        Set heritage status (bien interes cultural).

        Optionally, with start date qualifier.
        """
        heritage = self.mapping["heritage"]["item"]
        if self.has_non_empty_attribute("fecha"):
            # 20 de febrero de 1985
            qualifier = {}
            es_date = dateparser.parse(self.fecha, languages=['es'])
            if es_date:
                date_dict = utils.datetime_object_to_dict(es_date)
                qualifier = {"start_time": utils.package_time(date_dict)}
            else:
                self.add_to_report("fecha", self.fecha, "start_time")
            self.add_statement("heritage_status", heritage, qualifier)
        else:
            self.add_statement("heritage_status", heritage)

    def set_adm_location(self):
        adm_q = None
        municip_dic = self.data_files["municipalities"]
        province_dic = self.data_files["provinces"]
        if utils.count_wikilinks(self.municipio) == 1:
            adm_q = utils.q_from_first_wikilink("es", self.municipio)
        else:
            # sometimes they're in ''
            municip_raw = utils.remove_markup(self.municipio)
            municip_match = utils.get_item_from_dict_by_key(
                dict_name=municip_dic,
                search_term=municip_raw,
                search_in="itemLabel")

            if len(municip_match) == 1:
                adm_q = municip_match[0]
            else:
                self.add_to_report("municipio",
                                   self.municipio,
                                   "located_adm")
        if not adm_q:
            province_raw = self.provincia_iso.lower()
            prov_match = utils.get_item_from_dict_by_key(
                dict_name=province_dic,
                search_term=province_raw,
                search_in="itemLabel")
            if len(prov_match) == 1:
                adm_q = prov_match[0]
            else:
                self.add_to_report("provincia_iso",
                                   self.provincia_iso,
                                   "located_adm")

        if adm_q:
            self.add_statement("located_adm", adm_q)

    def set_special_is(self):
        is_dic = self.data_files["tipobic"]["mappings"]
        if self.has_non_empty_attribute("tipobic"):
            s_raw = self.tipobic.lower()
            s_match = utils.get_matching_items_from_dict(value=s_raw,
                                                         dict_name=is_dic)
            if len(s_match) == 1:
                self.remove_statement("is")
                self.add_statement("is", s_match[0])
            else:
                self.add_to_report("tipobic", self.tipobic, "is")

    def update_labels(self):
        spanish = utils.remove_markup(self.nombre)
        self.add_label("es", spanish)

    def update_descriptions(self):
        place = "Spain"
        if self.has_non_empty_attribute("municipio"):
            place = "{}, {}".format(utils.remove_markup(self.municipio), place)
        elif self.has_non_empty_attribute("lugar"):
            place = "{}, {}".format(utils.remove_markup(self.lugar), place)
        desc_dic = {"es": "Bien de Interés Cultural",
                    "en": "cultural property in {}".format(place)}
        for lg in desc_dic:
            self.add_description(lg, desc_dic[lg])

    def set_location(self):
        """
        Add location statement (P276).

        Extract possible location from wikilinked value.
        Run after set_adm_location and compared with
        its result, to avoid using the same statement
        for location and adm location.
        """
        if self.has_non_empty_attribute("lugar"):
            if utils.count_wikilinks(self.lugar) == 1:
                adm_loc = self.get_statement_values("located_adm")
                loc_q = utils.q_from_first_wikilink("es", self.lugar)
                if adm_loc and loc_q != adm_loc[0]:
                    self.add_statement("location", loc_q)
            else:
                self.add_to_report("lugar", self.lugar, "location")

    def set_heritage_id(self):
        """
        Set Bien Interes Cultural as heritage_id.

        Also use it as a distinguisher in case of duplicate
        label/description pairs.
        """
        self.add_disambiguator(str(self.bic), 'es')
        self.add_statement("bien_de_interes", str(self.bic))

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = self.bic

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        if self.bic in ["", "0", "-", "s/n"]:
            self.upload = False
            return
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_heritage_with_date()
        self.set_heritage_id()
        self.set_country()
        self.set_adm_location()
        self.set_location()
        self.set_is()
        self.set_special_is()
        self.set_coords(("lat", "lon"))
        self.set_commonscat()
        self.set_image("imagen")
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("es", "es", EsEs)
    dataset.data_files = {
        "municipalities": "spain_municipalities.json",
        "provinces": "spain_provinces.json"}
    dataset.lookup_downloads = {"tipobic": "es (es)/tipobic"}
    importer.main(args, dataset)
