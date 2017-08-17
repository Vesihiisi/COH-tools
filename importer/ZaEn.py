from Monument import Monument
import importer_utils as utils


class ZaEn(Monument):

    def set_monuments_all_id(self):
        self.monuments_all_id = self.sitereference

    def set_heritage_id(self):
        sahra = self.sitereference.replace("/", "")
        self.add_statement("sahra", sahra)

    def update_labels(self):
        name = utils.remove_markup(self.site_name)
        self.add_label("en", name)

    def set_adm_location(self):
        municip = self.magisterial_district
        admin_dic = self.data_files["administrative"]
        province_dic = self.data_files["provinces"]
        municip_match = [x["item"] for x in admin_dic if municip in x["itemLabel"]]
        if len(municip_match) == 0:
            prov_iso = self.province_iso
            province_match = [x["item"] for x in province_dic if x["iso"] == prov_iso]
            if len(province_match) == 1:
                self.add_statement("located_adm", province_match[0])
            else:
                self.add_to_report("magisterial_district", municip, "located_adm")
        elif len(municip_match) == 1:
            self.add_statement("located_adm", municip_match[0])
        else:
            self.add_to_report("magisterial_district", municip, "located_adm")

    def set_location(self):
        settlement_dic = self.data_files["settlements"]
        town_match = [x["item"] for x in settlement_dic if x["itemLabel"] == self.town]
        if len(town_match) == 1:
            self.add_statement("location", town_match[0])
        else:
            self.add_to_report("town", self.town, "location")

    def set_heritage(self):
        print(self.nhra_status, "---", self.nmc_status)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.update_labels()
        self.set_country()
        self.set_heritage_id()
        self.set_heritage()
        self.set_commonscat()
        self.set_image("image")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_location()
