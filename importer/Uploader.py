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

    def add_labels(self, target_item, labels):
        for label in labels:
            target_item.get()
            name = labels[label]['value']
            lang = labels[label]['language']
            self.wdstuff.addLabelOrAlias(
                lang, name, target_item, "label: " + name)

    def add_descriptions(self, target_item, descriptions):
        for description in descriptions:
            target_item.get()
            name = descriptions[description]['value']
            lang = descriptions[description]['language']
            if (not target_item.descriptions or
                    lang not in target_item.descriptions):
                descs = {lang: name}
                target_item.editDescriptions(descs)
                pywikibot.output("Added description: " + name)
        return

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

    def make_image_item(self, filename):
        commonssite = pywikibot.Site("commons", "commons")
        imagelink = pywikibot.Link(
            filename, source=commonssite, defaultNamespace=6)
        return pywikibot.FilePage(imagelink)

    def make_coords_item(self, coordstuple):
        """
        Default precision, such as used by
        http://pywikibot.readthedocs.io/en/latest/_modules/scripts/claimit/
        """
        DEFAULT_PREC = 0.0001
        return pywikibot.Coordinate(
            coordstuple[0], coordstuple[1], precision=DEFAULT_PREC)

    def make_quantity_item(self, quantity, repo):
        value = quantity['quantity_value']
        if quantity['unit']:
            unit = "http://www.wikidata.org/entity/" + quantity['unit']
        else:
            unit = None
        return pywikibot.WbQuantity(value, unit, site=repo)

    def make_time_item(self, quantity, repo):
        """
        This only works for full years.
        TODO
        Make it work for year range!
        """
        value = quantity['time_value']
        print(value)
        return pywikibot.WbTime(year=value)

    def make_q_item(self, qnumber):
        return self.wdstuff.QtoItemPage(qnumber)

    def make_pywikibot_item(self, value, prop=None, ):
        val_item = None
        if type(value) is list and len(value) == 1:
            value = value[0]
        if utils.string_is_q_item(value):
            val_item = self.make_q_item(value)
        elif prop == PROPS["image"] and utils.file_is_on_commons(value):
            val_item = self.make_image_item(value)
        elif utils.tuple_is_coords(value) and prop == PROPS["coordinates"]:
            val_item = self.make_coords_item(value)
        elif isinstance(value, dict) and 'quantity_value' in value:
            print("detected quantity")
            val_item = self.make_quantity_item(value, self.repo)
        elif isinstance(value, dict) and 'time_value' in value:
            print("detected year")
            val_item = self.make_time_item(value, self.repo)
        elif prop == PROPS["commonscat"] and utils.commonscat_exists(value):
            val_item = value
        else:
            val_item = value
        return val_item

    def make_statement(self, value):
        return self.wdstuff.Statement(value)

    def make_url_reference(self, uri):
        prop = PROPS["reference_url"]
        ref = self.wdstuff.Reference(
            source_test=self.wdstuff.make_simple_claim(prop, uri))
        return ref

    def add_claims(self, wd_item, claims):
        if wd_item:
            for claim in claims:
                prop = claim
                for x in claims[claim]:
                    print(prop)
                    print(x)
                    value = x['value']
                    if value != "":
                        ref = None
                        quals = x['quals']
                        refs = x['refs']
                        wd_claim = self.make_pywikibot_item(value, prop)
                        wd_value = self.make_statement(wd_claim)
                        if any(quals):
                            for qual in quals:
                                value = self.make_pywikibot_item(
                                    quals[qual], qual)
                                qualifier = self.wdstuff.Qualifier(qual, value)
                                wd_value.addQualifier(qualifier)
                        if len(refs) > 0:
                            for ref in refs:
                                """
                                This only works if it's a url.
                                If we have references of different sort,
                                this will have to be appended.
                                """
                                if utils.is_valid_url(ref):
                                    ref = self.make_url_reference(ref)
                        if wd_value:
                            print("")
                            print("Added value: ", prop)
                            self.wdstuff.addNewClaim(
                                prop, wd_value, wd_item, ref)

    def upload(self):
        labels = self.make_labels()
        descriptions = self.make_descriptions()
        claims = self.data["statements"]
        exists = True if self.data["wd-item"] is not None else False
        if exists:
            # item_q = self.data["wd-item"]
            target_item = self.wdstuff.QtoItemPage(self.TEST_ITEM)
            print(target_item)
        else:
            # print("new item created here...")
            target_item = self.wdstuff.QtoItemPage(self.TEST_ITEM)
            # target_item = self.create_new_item()
        self.add_labels(target_item, labels)
        self.add_descriptions(target_item, descriptions)
        self.add_claims(target_item, claims)
