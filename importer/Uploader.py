from wikidataStuff.WikidataStuff import WikidataStuff as WDS
import pywikibot
import importer_utils as utils
from os import path

MAPPING_DIR = "mappings"
PROPS = utils.load_json(path.join(MAPPING_DIR, "props_general.json"))

class Uploader(object):

    TEST_ITEM = "Q4115189"

    def make_labels(self):
        labels = self.data["labels"]
        new_labels = {}
        for item in labels:
            new_labels[item] = {'language': item, 'value': labels[item]}
        return new_labels

    def make_descriptions(self):
        descriptions = self.data["descriptions"]
        new_descriptions = {}
        for item in descriptions:
            new_descriptions[item] = {
                'language': item, 'value': descriptions[item]}
        return new_descriptions

    def __init__(self, monument_object):
        self.data = monument_object.wd_item
        site = pywikibot.Site("wikidata", "wikidata")
        self.repo = site.data_repository()
        self.wdstuff = WDS(self.repo)

    def make_pywikibot_item(self, value, prop=None, ):
        """
        TODO
        Process values like:
        * time value
        * Commonscat
        """
        val_item = None
        if utils.string_is_q_item(value):
            val_item = self.wdstuff.QtoItemPage(value)
        elif prop == PROPS["image"] and utils.file_is_on_commons(value):
            """
            TODO
            Separate this out
            """
            print("---------------- IMAGE!")
            commonssite = pywikibot.Site("commons", "commons")
            imagelink = pywikibot.Link(value, source=commonssite, defaultNamespace=6)
            val_item = pywikibot.FilePage(imagelink)
        elif utils.tuple_is_coords(value) and prop == PROPS["coordinates"]:
            print("COORDINATES: ", value)
            """
            TODO
            Move to separate method
            Default precision, such as used by http://pywikibot.readthedocs.io/en/latest/_modules/scripts/claimit/
            """
            val_item = pywikibot.Coordinate(value[0], value[1], precision=0.0001)
        elif isinstance(value, float) or isinstance(value, int):
            val_item = pywikibot.WbQuantity(value, site=self.repo)
        else:
            val_item = value
        return val_item

    def make_statement(self, value):
        return self.wdstuff.Statement(value)

    def add_claims(self, wd_item, claims):
        if wd_item:
            item_dict = wd_item.get()
            for claim in claims:
                prop = claim
                for x in claims[claim]:
                    print(x)
                    value = x['value']
                    if len(value) > 0:
                        quals = x['quals']
                        refs = x['refs']
                        wd_value = self.make_statement(self.make_pywikibot_item(value, prop))
                        if any(quals):
                            print("!!!!!!!there are some qualifiers....")
                            for qual in quals:
                                value = self.make_pywikibot_item(quals[qual], qual)
                                qualifier = self.wdstuff.Qualifier(qual, value)
                                wd_value.addQualifier(qualifier)
                        if len(refs) > 0:
                            print("there are some references....")
                        if wd_value:
                            print("")
                            #print(wd_value)
                            self.wdstuff.addNewClaim(prop, wd_value, wd_item, None)

    def upload(self):
        labels = self.make_labels()
        descriptions = self.make_descriptions()
        claims = self.data["statements"]
        exists = True if self.data["wd-item"] is not None else False
        if exists:
            item_q = self.data["wd-item"]
            target_item = self.wdstuff.QtoItemPage(self.TEST_ITEM)
            print(target_item)
        else:
            # print("new item created here...")
            target_item = self.wdstuff.QtoItemPage(self.TEST_ITEM)
            # target_item = self.create_new_item()
        # TODO self.add_labels
        # TODO self.add_descriptions
        self.add_claims(target_item, claims)
