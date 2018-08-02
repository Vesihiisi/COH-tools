from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer
import requests
from os import path


MAPPING_DIR = "mappings"


class SeBbrSv(Monument):

    def update_labels(self):
        """
        Set the label in Swedish.

        Original labels look like this:
            Wickmanska gården (Paradis 35)
        We don't need the latter part (fastighetsbeteckning) in the label.

        If there's an error in parsing the brackets,
        use the raw version.
        """
        clean_name = utils.remove_markup(self.namn)
        try:
            label = utils.get_rid_of_brackets(clean_name)
        except ValueError:
            label = clean_name
            self.add_to_report("malformed_label", self.namn)
        self.add_label("sv", label)

    def create_bbr_link(self):
        """
        Create BBR link.

        This will get a link that looks like
            raa/bbr/21300000002805
        Depending on whether the prefix is raa/bbr/ or raa/bbra/
        """
        self.bbr_link = utils.get_bbr_link(self.bbr)

    def set_bbr(self):
        """Set the BBR ID property."""
        self.add_statement("cultural_heritage_sweden", self.bbr_link)

    def get_online_data(self):
        """
        Retrieve online data about BBR complex.

        This includes, inter alia, the legal protection
        status and ID's of each part of the
        compound.
        """
        h_property = self.props["cultural_heritage_sweden"]
        self.kulturarv_id = self.wd_item["statements"][h_property][0]["value"]
        url = "http://kulturarvsdata.se/{}".format(self.kulturarv_id)
        print("Retrieving online data from {}".format(url))
        # http://kulturarvsdata.se/raa/bbr/21300000023251
        url_list = url.split("/")
        url_list.insert(-1, "jsonld")
        url = "/".join(url_list)
        # Request data in json format
        # http://kulturarvsdata.se/raa/bbr/jsonld/21300000023251
        data = requests.get(url)
        try:
            result = data.json()
        except ValueError:
            result = None
        self.online_data = result

    def get_has_parts(self):
        """Get any parts listed in online data."""
        results = []
        for element in self.online_data["@graph"]:
            if "hasPart" in element:
                results.extend(element["hasPart"])
        return results

    def set_heritage_bbr(self):
        """
        Set the specific type of heritage status.

        In Sweden there are three different types of legal protection
        for different types of cultural heritage,
        so we created three new items:

        governmental listed building complex (Q24284071)
        for buildings owned by the state,

        individual listed building complex (Q24284072)
        for privately owned buildings,

        ecclesiastical listed building complex (Q24284073)
        for older buildings owned by the Church of Sweden.
        """
        type_q = None
        protection_date = False
        if self.online_data is None:
            self.add_to_report("invalid_bbr_url", self.bbr_link)
            return
        for element in self.online_data["@graph"]:
            if "ns5:spec" in element:
                bbr_type = element["ns5:spec"]
                if bbr_type.startswith("Kyrkligt kulturminne"):
                    # Kyrkligt kulturminne. 4 kap. KML -- these don't seem to
                    # have dates
                    type_q = "Q24284073"
                elif bbr_type.startswith("Byggnadsminne"):
                    # Byggnadsminne (BM) 3 kap. KML (1977-02-25)
                    type_q = "Q24284072"
                    protection_date = bbr_type.split("(")[-1][:-1]
                elif bbr_type.startswith("Statligt byggnadsminne"):
                    # Statligt byggnadsminne (SBM). Förordning (2013:558)
                    # (1935-01-25)
                    type_q = "Q24284071"
                    protection_date = bbr_type.split("(")[-1][:-1]
        # The original set_heritage() added an empty claim
        # because there's no heritage status specified in mapping file,
        # so we start by removing that empty claim.
        self.remove_statement("heritage_status")
        qualifier = None
        if protection_date:
            # 1969-01-31
            try:
                date_dict = utils.date_to_dict(protection_date, "%Y-%m-%d")
                qualifier = {"start_time": utils.package_time(date_dict)}
            except ValueError:
                self.add_to_report("protection_type", bbr_type)
        url = "http://kulturarvsdata.se/{}".format(self.kulturarv_id)
        kulturarv_source = self.create_kulturarv_source(url)
        if type_q:
            self.add_statement(
                "heritage_status", type_q, qualifier, refs=[kulturarv_source])
        else:
            self.add_to_report("heritage_status",
                               self.kulturarv_id,
                               "heritage_status")

    def create_kulturarv_source(self, url):
        """
        Create a reference to the BBR database.

        The reference is used to source the heritage status
        statement. It contains a link to the item in the open
        API kulturarvsdata.se.
        """
        source_item = self.sources["bebyggelseregistret"]
        today = utils.today_dict()
        prop_reference_url = self.props["reference_url"]
        prop_date = self.props["retrieved"]
        prop_stated = self.props["stated_in"]
        prop_reference_url = self.props["reference_url"]
        kulturarv_source = {
            "source": {"prop": prop_stated, "value": source_item},
            "published": {"prop": prop_date, "value": today},
            "reference_url": {"prop": prop_reference_url, "value": url}}
        return kulturarv_source

    def set_function(self):
        """
        Set the use (P366) property.

        Extract the functions from the 'funktion' field,
        whose contents look like 'Kyrka med kyrkotomt,Skola (1 byggnad)'.
        Use the mapping table:
        https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/se-bbr_(sv)/functions
        """
        functions_map = self.data_files["functions"]["mappings"]
        if self.has_non_empty_attribute("funktion"):
            functions_string = utils.get_rid_of_brackets(self.funktion)
            functions = functions_string.lower().split(",")
            for item in functions:
                function = item.strip()
                try:
                    function_item = [functions_map[x]["items"]
                                     for x in functions_map if
                                     x.lower() == function]
                    function_item_clean = function_item[0][0]
                    self.add_statement("use", function_item_clean)
                except IndexError:
                    data_string = "{} ({})".format(function, self.funktion)
                    # report both this particular function and the whole
                    # string containing it
                    self.add_to_report("funktion", data_string, "use")

    def set_architect(self):
        """
        Set the architect.

        Only if wikilinked.
        Can be more than one.
        Check if it's a human.
        """
        if self.has_non_empty_attribute("arkitekt"):
            architects = utils.get_wikilinks(self.arkitekt)
            for name in architects:
                wp_page = name.title
                q_item = utils.q_from_wikipedia("sv", wp_page)
                if q_item:
                    if utils.is_whitelisted_P31(q_item, self.repo, ["Q5"]):
                        self.add_statement("architect", q_item)
                    else:
                        self.add_to_report("arkitekt", self.arkitekt)

    def set_location(self):
        """
        Set location or street address.

        There are some street addresses. Some are simple:
            Norra Murgatan 3
        Some are complex:
            Skolgatan 5, Västra Kyrkogatan 3
            Norra Murgatan 27, Uddens gränd 14-16

        If self.plats consists of 1 wikilinked item,
        get the WD item and cross check with the list of
        known human settlements.

        If it's not wikilinked text, try to extract an address.
        """
        settlements_dict = self.data_files["settlements"]
        if self.has_non_empty_attribute("plats"):
            if utils.count_wikilinks(self.plats) == 1:
                location_q = utils.q_from_first_wikilink("sv", self.plats)
                try:
                    legit_location = [x["item"] for
                                      x in settlements_dict if
                                      x["item"] == location_q]
                    legit_location_clean = legit_location[0]
                    self.add_statement("location", legit_location_clean)
                except IndexError:
                    self.add_to_report("plats", self.plats)
            elif utils.count_wikilinks(self.plats) == 0:
                processed_address = utils.get_street_address(self.plats, "sv")
                if processed_address:
                    self.add_statement("located_street", processed_address)
                else:
                    self.add_to_report("plats", self.plats)
            else:
                self.add_to_report("plats", self.plats)

    def update_descriptions(self):
        """
        Add the fastighetsbeteckning as alias.

        For example:
            (Knutse 2:19)

        If there's an error in parsing the brackets,
        use the raw version.
        """
        try:
            fastighetsbeteckning = utils.get_text_inside_brackets(self.namn)
        except ValueError:
            fastighetsbeteckning = self.namn
            self.add_to_report("malformed_label", self.namn)
        self.add_alias("sv", fastighetsbeteckning)

    def get_no_of_buildings(self):
        return utils.get_number_from_string(
            utils.get_text_inside_brackets(self.funktion))

    def set_no_of_buildings(self):
        """
        Set how many buildings the item consists of.

        The 'funktion' column looks like this:
            Kapell (3 byggnader)
        From this, we extract: has parts of class building,
        and how many as qualifier.
        Some items don't have any numbers, so we ignore those.
        """
        buildings = self.get_no_of_buildings()
        if buildings:
            self.add_statement(
                "has_parts_of_class", "Q41176",
                utils.package_quantity(buildings))

    def set_adm_location(self):
        """
        Set the administrative location.

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
            self.add_to_report("kommun", self.kommun, "located_adm")

    def set_inception(self):
        """
        Set the building year.

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
            if isinstance(year_parsed, int):
                date_dict = {"year": year_parsed}
                self.add_statement("inception", utils.package_time(date_dict))

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = self.bbr

    def exists_with_monument_article(self, language):
        """Set language of Wikipedia to use to match articles."""
        return super().exists_with_monument_article("sv")

    def get_wditems_bbr_links(self):
        """
        Get BBR links of associated WD item.

        If the data object is associated
        with a WD item, check if it has P1260
        of the type raa/bbr(a) and get their
        values.
        """
        result = []
        associated_item = self.wd_item["wd-item"]
        if associated_item:
            heritage_links = utils.get_value_of_property(
                associated_item, "P1260", self.repo)
            for link in heritage_links:
                if link.startswith("raa/bbr"):
                    result.append(link)
            return result

    def check_wd_item(self):
        """
        Detect BBR conflict in associated WD item.

        Get any P1260 of associated WD item.

        If it's 1 BBR building link AND the compound consists of 1 building,
        and the link is the same as the link to that building,
        keep the item association.

        If it's a BBR ID that's different
        from the one in the data object,
        remove the association. Data will be uploaded
        to a newly created WD item instead.
        """
        bbr_url_on_wd = self.get_wditems_bbr_links()
        parts_of_compound = self.get_has_parts()
        if len(bbr_url_on_wd) == 1:
            if bbr_url_on_wd[0] == self.bbr_link:
                return
            elif len(parts_of_compound) == 1:
                if parts_of_compound[0] == bbr_url_on_wd[0]:
                    return
        elif len(bbr_url_on_wd) == 2:
            if len(parts_of_compound) == 1:
                if all(entry in bbr_url_on_wd
                       for entry in [parts_of_compound[0], self.bbr_link]):
                    return
        elif len(bbr_url_on_wd) == 0:
            return
        self.wd_item["wd-item"] = None

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.create_bbr_link()
        self.set_bbr()
        self.get_online_data()
        self.set_country()
        self.set_is()
        self.set_heritage()
        self.set_source()
        self.set_registrant_url()
        self.update_labels()
        self.update_descriptions()
        self.set_image("bild")
        self.set_commonscat()
        self.set_coords(("lat", "lon"))
        self.set_inception()
        self.set_no_of_buildings()
        self.set_heritage_bbr()
        self.set_adm_location()
        self.set_architect()
        self.set_location()
        self.set_function()
        self.set_wd_item(self.find_matching_wikidata(mapping))
        self.check_wd_item()


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("se-bbr", "sv", SeBbrSv)
    dataset.data_files = {
        "functions": "se-bbr_(sv)_functions.json",
        "settlements": "sweden_settlements.json"}
    importer.main(args, dataset)
