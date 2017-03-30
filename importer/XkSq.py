from Monument import Monument
import importer_utils as utils


class XkSq(Monument):

    def update_labels(self):
        """
        Set the labels.

        TODO
        Some of these contain several unprintable characters...
        0093 - 0096
        Maybe just go to the article and remove them?
        https://sq.wikipedia.org/wiki/Lista_e_Monumenteve_n%C3%AB_Kosov%C3%AB
        """
        print(self.name)
        return

    def set_no(self):
        self.add_statement("kosovo_monument_id", str(self.idno))

    def set_adm_location(self):
        """
        Set the administrative location.

        The values are never wikilinked.
        E panjohur = unknown
        """
        print(self.municipality)

    def update_commonscat(self):
        """
        Set the Commons category property.

        The actual category names are not saved
        in the database, BUT
        a full category tree exists on commons,
        even though many of the cats are empty:
        https://commons.wikimedia.org/wiki/Category:Cultural_heritage_monuments_in_Kosovo_with_ID_No_3340
        These can be deduced from ID number
        """
        PATTERN = "Cultural heritage monuments in Kosovo with ID No "
        category = PATTERN + self.idno
        if utils.commonscat_exists(category):
            self.add_statement("commonscat", category)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        self.exists("sq")
        self.update_commonscat()
        self.set_image("image")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_no()
        # self.set_location()
        # self.set_sagsnr()
        # self.set_address()
        # self.set_inception()
        self.exists_with_prop(mapping)
        # self.print_wd()
