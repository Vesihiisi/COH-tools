from Monument import Monument
import importer_utils as utils


class DkFortidsDa(Monument):

    def update_labels(self):
        """
        TODO: Naming things!
        See:
        https://da.wikipedia.org/wiki/Fredede_fortidsminder_i_Ikast-Brande_Kommune
        The monuments don't have unique names, stednavn
        is a general placename.
        Use the description field to provide better info:
        'rundhøj i Ikast-Brande kommune'
        """
        self.add_label("da", utils.remove_markup(self.stednavn))

    def update_descriptions(self):
        monument_type = utils.remove_markup(self.type).lower()
        municipality = utils.remove_markup(self.kommune)
        description_da = "{} i {}".format(monument_type, municipality)
        self.add_description("da", description_da)

    def set_adm_location(self):
        if self.has_non_empty_attribute("kommune"):
            if utils.count_wikilinks(self.kommune) == 1:
                adm_location = utils.q_from_first_wikilink("da", self.kommune)
                self.add_statement("located_adm", adm_location)

    def set_type(self):
        if self.has_non_empty_attribute("type"):
            table = self.data_files["types"]["mappings"]
            try:
                special_type = [table[x]["items"]
                                for x in table
                                if x == self.type][0]
                self.substitute_statement("is", special_type)
            except IndexError:
                return

    def set_inception(self):
        """
        TODO
        these are very broad...
        basically "prehistoric time", "modern time"
        is this even useful?
        """
        if self.has_non_empty_attribute("datering"):
            if len(utils.get_wikilinks(self.datering)) == 1:
                print(self.datering)
                print(utils.q_from_first_wikilink("da", self.datering))

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        self.update_descriptions()
        self.exists("da")
        self.set_commonscat()
        self.set_image("billede")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_type()
        # self.set_inception()
        # self.set_location()
        # self.set_sagsnr()
        # self.set_address()
        # self.set_inception()
        # self.print_wd()
        self.exists_with_prop(mapping)
