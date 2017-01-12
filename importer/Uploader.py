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

    def add_labels(self, labels):
        print(labels)

    def add_descriptions(self, descriptions):
        print(descriptions)

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
        if type(value) is list and len(value) == 1:
            value = value[0]
        if utils.string_is_q_item(value):
            val_item = self.wdstuff.QtoItemPage(value)
        elif prop == PROPS["image"] and utils.file_is_on_commons(value):
            """
            TODO
            Separate this out
            """
            print("---------------- IMAGE!")
            commonssite = pywikibot.Site("commons", "commons")
            imagelink = pywikibot.Link(
                value, source=commonssite, defaultNamespace=6)
            val_item = pywikibot.FilePage(imagelink)
        elif utils.tuple_is_coords(value) and prop == PROPS["coordinates"]:
            print("COORDINATES: ", value)
            """
            TODO
            Move to separate method
            Default precision, such as used by http://pywikibot.readthedocs.io/en/latest/_modules/scripts/claimit/
            """
            val_item = pywikibot.Coordinate(
                value[0], value[1], precision=0.0001)
        elif isinstance(value, float) or isinstance(value, int):
            val_item = pywikibot.WbQuantity(value, site=self.repo)
        elif prop == PROPS["commonscat"] and utils.commonscat_exists(value):
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! commonscat")
            val_item = value
        else:
            val_item = value
        return val_item

    def make_statement(self, value):
        return self.wdstuff.Statement(value)

    def make_url_reference(self, uri):
        ref = self.wdstuff.Reference(
            source_test=self.wdstuff.make_simple_claim(PROPS["reference_url"], uri))
        return ref

    def add_claims(self, wd_item, claims):
        if wd_item:
            item_dict = wd_item.get()
            for claim in claims:
                prop = claim
                for x in claims[claim]:
                    print(prop)
                    print(x)
                    value = x['value']
                    if len(value) > 0:
                        ref = None
                        quals = x['quals']
                        refs = x['refs']
                        wd_claim = self.make_pywikibot_item(value, prop)
                        wd_value = self.make_statement(wd_claim)
                        if any(quals):
                            print("!!!!!!!there are some qualifiers....")
                            for qual in quals:
                                value = self.make_pywikibot_item(
                                    quals[qual], qual)
                                qualifier = self.wdstuff.Qualifier(qual, value)
                                wd_value.addQualifier(qualifier)
                        if len(refs) > 0:
                            print("!!!!!!!!there are some references....")
                            for ref in refs:
                                """
                                When it's not a url but an item
                                """
                                if utils.is_valid_url(ref):
                                    ref = self.make_url_reference(ref)
                        if wd_value:
                            print("")
                            # print(wd_value)
                            self.wdstuff.addNewClaim(prop, wd_value, wd_item, ref)

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
        self.add_labels(labels)
        self.add_descriptions(descriptions)
        self.add_claims(target_item, claims)
