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
            es_date = dateparser.parse(self.fecha, languages=['es'])
            try:
                date_dict = utils.datetime_object_to_dict(es_date)
                print(date_dict)
            except ValueError:
                self.add_to_report("fecha", self.fecha)
                self.add_statement("heritage_status", heritage)
                return
            qualifier = {"start_time": {"time_value": date_dict}}
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
            municip_match = [x for x in municip_dic if x[
                "itemLabel"] == municip_raw]
            if len(municip_match) == 1:
                adm_q = municip_match[0]["item"]
        if not adm_q:
            province_raw = self.provincia_iso.lower()
            prov_match = [x for x in province_dic if x[
                "itemLabel"].lower() == province_raw]
            if len(prov_match) == 1:
                adm_q = prov_match[0]["item"]

        if adm_q:
            self.add_statement("located_adm", adm_q)
        else:
            self.add_to_report("municipio", self.municipio, "located_adm")

    def set_special_is(self):
        is_dic = self.data_files["tipobic"]["mappings"]
        if self.has_non_empty_attribute("tipobic"):
            special_raw = self.tipobic.lower()
            special_match = [is_dic[x]
                             for x in is_dic if x.lower() == special_raw]
            if len(special_match) == 1:
                self.remove_statement("is")
                special_types = special_match[0]["items"]
                for s in special_types:
                    self.add_statement("is", s)

    def update_labels(self):
        spanish = utils.remove_markup(self.nombre)
        self.add_label("es", spanish)

    def update_descriptions(self):
        desc_dic = {"es": "Bien de Interés Cultural",
                    "en": "cultural property in Spain"}
        for lg in desc_dic:
            self.add_description(lg, desc_dic[lg])

    def set_location(self):
        if self.has_non_empty_attribute("lugar"):
            if utils.count_wikilinks(self.lugar) == 1:
                adm_loc = self.wd_item["statements"]["P131"][0]["value"]
                loc_q = utils.q_from_first_wikilink("es", self.lugar)
                if loc_q != adm_loc:
                    self.add_statement("location", loc_q)
            else:
                self.add_to_report("lugar", self.lugar, "location")

    def set_heritage_id(self):
        self.add_statement("bien_de_interes", str(self.bic))

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = self.bic

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("es", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
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
