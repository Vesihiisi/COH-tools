from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class EeEt(Monument):

    def set_descriptions(self):
        """Add descriptions in Swedish and English."""
        short_d = {"en": "cultural property in Estonia",
                   "sv": "kulturarv i Estland"}
        long_d = {
            "en": "cultural property in {}, Estonia",
            "sv": "kulturarv i {}, Estland"
        }
        if self.has_non_empty_attribute("omavalitsus"):
            municip = self.omavalitsus
            for language in long_d:
                self.add_description(
                    language, long_d[language].format(municip))
        else:
            for language in short_d:
                self.add_description(language, short_d[language])

    def update_heritage(self):
        """
        Substitute default heritage property with specific one.

        Cultural properties can have one or more specific
        types: https://et.wikipedia.org/wiki/Kultuurim%C3%A4lestis

        Use the mapping table:
        https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/ee_(et)/types
        to substitute the generic type, if applicable.
        """
        if self.has_non_empty_attribute("liik"):
            special_heritage = self.liik.lower()
            glossary = self.data_files["heritage_types"]["mappings"]
            try:
                heritage = [glossary[x]["items"]
                            for x in glossary
                            if x.lower() == special_heritage]
                if len(heritage[0]) > 0:
                    self.remove_statement("heritage_status")
                    for typ in heritage[0]:
                        self.add_statement("heritage_status", typ)
            except IndexError:
                return

    def set_heritage_id(self):
        """Set Estonian cultural monument ID (P2948)."""
        self.add_statement("estonian_monument_id", self.number)

    def set_adm_location(self):
        """
        Set the administrative location.

        Match the omavalitsus to item in offline list;
        try both with and without "vald" as not all
        labels have it.
        """
        if self.maakond.lower() == "territoriaalmeri":
            # territorial waters - stuff like shipwrecks
            return
        try:
            municip = self.omavalitsus
            glossary = self.data_files["municipalities"]
            municip_item = [x["item"]
                            for x in glossary
                            if x["itemLabel"] == municip]
            if len(municip_item) == 0 and "vald" not in municip:
                municip = municip + " vald"
                municip_item = [x["item"]
                                for x in glossary
                                if x["itemLabel"] == municip]
            self.add_statement("located_adm", municip_item[0])
        except IndexError:
            self.add_to_report("omavalitsus", self.omavalitsus, "located_adm")

    def set_location(self):
        """
        Set the location property, P276, based on aadress.

        Despite its name, aadress does not always contain
        address-like data. That's why we don't use it for
        anything if it contains only text.
        It's only used if it contains 1 unique wikilink;
        sometimes it contains multiple instances of the same
        wikilink e.g.
            [[Võsivere|Võsivere küla]], Janise,
            [[Võsivere|Võsivere küla]], Mossi,
            [[Võsivere|Võsivere küla]], Rätsepa, [[Võsivere|Võsivere küla]], Tilmani,
            [[Võsivere|Võsivere küla]], Viskaja(5)
        As the content of one field. This will be counted as 1 wikilink.

        The WD item associated with the wikilink
        is then matched with a list of Estonian settlements,
        and if there's a match, it's added as 'location'.
        """
        location_raw = self.aadress  # very often not an address....
        wikilinks = utils.get_unique_wikilinks(location_raw)
        if len(wikilinks) == 1:
            glossary = self.data_files["settlements"]
            target_name = wikilinks[0].title
            target_item = utils.get_item_from_dict_by_key(dict_name=glossary,
                                                          search_term=target_name,
                                                          search_in="itemLabel",)
            if len(target_item) == 1:
                self.add_statement("location", target_item[0])
            else:
                self.add_to_report("aadress", self.aadress, "location")
        else:
            self.add_to_report("aadress", self.aadress, "location")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_changed()
        self.set_monuments_all_id("number")
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_heritage()
        self.set_coords()
        self.set_commonscat()
        self.set_image("pilt")
        self.set_country()
        self.set_adm_location()
        self.update_heritage()
        self.set_is()
        self.set_location()
        self.set_labels("et", self.nimi)
        self.set_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("ee", "et", EeEt)
    dataset.data_files = {
        "municipalities": "estonia_municipalities.json",
        "settlements": "estonia_settlements.json",
        "counties": "estonia_counties.json"
    }
    dataset.lookup_downloads = {
        "heritage_types": "ee (et)/types"
    }
    importer.main(args, dataset)
