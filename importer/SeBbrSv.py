from Monument import Monument
import importer_utils as utils
import requests
from os import path


MAPPING_DIR = "mappings"


class SeBbrSv(Monument):

    def update_labels(self):
        """
        Original labels look like this:
            Wickmanska gården (Paradis 35)
        We don't need the latter part (fastighetsbeteckning) in the label.
        """
        label = utils.get_rid_of_brackets(utils.remove_markup(self.namn))
        self.add_label("sv", label)
        return

    def set_bbr(self):
        """
        This will get a link that looks like
            raa/bbr/21300000002805
        Depending on whether the prefix is raa/bbr/ or raa/bbra/
        """
        bbr_link = utils.get_bbr_link(self.bbr)
        self.add_statement("bbr", bbr_link)

    def set_heritage_bbr(self):
        """
        In Sweden there are three different types of legal protection
        for different types of cultural heritage,
        so we created three new items:

        governmental listed building complex (Q24284071)
        for buildings owned by the state,

        individual listed building complex (Q24284072)
        for privately owned buildings,

        ecclesiastical listed building complex (Q24284073)
        for older buildings owned by the Church of Sweden.

        Which legal protection each monument goes under
        is not stored in the WLM database.
        We therefore need to look that up by
        querying the source database via their API.
        """
        url = "http://kulturarvsdata.se/" + \
            self.wd_item["statements"][self.props["bbr"]][0]["value"]
        url_list = url.split("/")
        url_list.insert(-1, "jsonld")
        url = "/".join(url_list)
        data = requests.get(url).json()
        for element in data["@graph"]:
            if "ns5:spec" in element:
                protection_date = False
                bbr_type = element["ns5:spec"]
                if bbr_type.startswith("Kyrkligt kulturminne"):
                    type_q = "Q24284073"
                elif bbr_type.startswith("Byggnadsminne"):
                    type_q = "Q24284072"
                    protection_date = bbr_type.split("(")[-1][:-1]
                elif bbr_type.startswith("Statligt byggnadsminne"):
                    type_q = "Q24284071"
                    protection_date = bbr_type.split("(")[-1][:-1]
        """
        The original set_heritage() added an empty claim
        because there's no heritage status specified in mapping file,
        so we start by removing that empty claim.
        """
        self.remove_claim("heritage_status")
        if protection_date:
            # 1969-01-31
            date_dict = utils.date_to_dict(protection_date, "%Y-%m-%d")
            qualifier = {"start_time":
                         {"time_value": date_dict}}
        else:
            qualifier = None
        self.add_statement("heritage_status", type_q, qualifier)

    def set_function(self):
        """
        TODO
        examples:
        https://gist.github.com/Vesihiisi/f637916ea1d80a4be5d71a3adf6e2dc2
        """
        # functions = get_rid_of_brackets(self.funktion).lower().split(",")
        return

    def set_architect(self):
        """
        Add architect claim if available.
        Only if wikilinked.
        Can be more than one.
        """
        if self.has_non_empty_attribute("arkitekt"):
            architects = utils.get_wikilinks(self.arkitekt)
            for name in architects:
                wp_page = name.title
                q_item = utils.q_from_wikipedia("sv", wp_page)
                if q_item is not None:
                    self.add_statement("architect", q_item)

    def set_location(self):
        """
        TODO
        This is the same as 'address' in monuments_all.
        There are some street addresses. Some are simple:
            Norra Murgatan 3
        Some are complex:
            Skolgatan 5, Västra Kyrkogatan 3
            Norra Murgatan 27, Uddens gränd 14-16
        """
        if self.has_non_empty_attribute("plats"):
            if utils.count_wikilinks(self.plats) == 1:
                location = utils.q_from_first_wikilink("sv", self.plats)
                self.add_statement("location", location)

    def update_descriptions(self):
        """
        Use fastighetsbeteckning as alias.
        For example:
            (Knutse 2:19)
        """
        fastighetsbeteckning = utils.get_text_inside_brackets(self.namn)
        self.add_alias("sv", fastighetsbeteckning)

    def set_no_of_buildings(self):
        """
        The 'funktion' column looks like this:
            Kapell (3 byggnader)
        From this, we extract: has parts of class building,
        and how many as qualifier.
        Some items don't have any numbers, so we ignore those.
        """
        extracted_no = utils.get_number_from_string(
            utils.get_text_inside_brackets(self.funktion))
        if extracted_no is not None:
            self.add_statement(
                "has_parts_of_class", "Q41176",
                {"quantity": {"quantity_value": extracted_no}})

    def set_adm_location(self):
        """
        Use offline mapping file
        to map municipality to P131.
        The column is 'kommun'.
        It looks like this:
            Alingsås
        Just the name of the municipality
        without the word kommun or genitive.
        """
        if self.kommun == "Göteborg":
            municip_name = "Gothenburg"
        else:
            municip_name = self.kommun
        municip_dict = utils.load_json(path.join(
            MAPPING_DIR, "sweden_municipalities.json"))
        pattern_en = municip_name.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "en"].lower() == pattern_en][0]
            self.add_statement("located_adm", municipality)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.kommun))
            return

    def set_inception(self):
        """
        The 'byggar' column can have many forms,
        but here we only process the obvious cases:
            1865
            [[1865]]
        It can also look like:
            1100- eller 1200-talet
        and many other variants, which are ignored.
        """
        if self.has_non_empty_attribute("byggar"):
            year_parsed = utils.parse_year(self.byggar)
            if year_parsed is not None:
                self.add_statement("inception", {"time_value": year_parsed})

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        self.update_descriptions()
        self.set_image("bild")
        self.exists("sv")
        self.set_commonscat()
        self.set_type()
        self.set_coords(("lat", "lon"))
        self.set_inception()
        self.set_no_of_buildings()
        self.set_bbr()
        self.set_heritage_bbr()
        self.set_adm_location()
        self.set_architect()
        self.set_location()
        self.set_function()
        self.exists_with_prop(mapping)
