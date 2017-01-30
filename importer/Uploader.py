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

    def make_aliases(self):
        aliases = self.data["aliases"]
        new_aliases = []
        for item in aliases:
            language = item
            for value in aliases[language]:
                new_alias = {"language": language, "value": value}
                new_aliases.append(new_alias)
        return new_aliases

    def add_labels(self, target_item, labels, log):
        for label in labels:
            target_item.get()
            name = labels[label]['value']
            lang = labels[label]['language']
            self.wdstuff.addLabelOrAlias(
                lang, name, target_item, "label: " + name)
            if log:
                t_id = target_item.getID()
                message = t_id + " ADDED LABEL " + lang + " " + name
                log.logit(message)

    def add_descriptions(self, target_item, descriptions, log):
        for description in descriptions:
            target_item.get()
            name = descriptions[description]['value']
            lang = descriptions[description]['language']
            if (not target_item.descriptions or
                    lang not in target_item.descriptions):
                descs = {lang: name}
                target_item.editDescriptions(descs)
                pywikibot.output("Added description: " + name)
                if log:
                    t_id = target_item.getID()
                    log.logit(t_id + " ADDED DESCRIPTION " + lang + " " + name)

    def add_aliases(self, target_item, aliases, log):
        for alias in aliases:
            print(alias)
            target_item.get()
            name = alias["value"]
            language = alias["language"]
            t_aliases = target_item.aliases
            if language in t_aliases and name in t_aliases[language]:
                return
            else:
                target_item.editAliases({language: [name]})
            if log:
                t_id = target_item.getID()
                log.logit(t_id + " ADDED ALIAS " + language + " " + name)

    def make_descriptions(self):
        descriptions = self.data["descriptions"]
        new_descriptions = {}
        for item in descriptions:
            new_descriptions[item] = {
                'language': item, 'value': descriptions[item]}
        return new_descriptions

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
        if 'unit' in quantity:
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
        return pywikibot.WbTime(**value)

    def make_q_item(self, qnumber):
        return self.wdstuff.QtoItemPage(qnumber)

    def item_has_prop(self, property_name, wd_item):
        """
        This is different from WikidataStuff has_claim()
        because it checks whether the property exists,
        not if the statement matches.
        If the target item already uses the property,
        a new claim will not be added even if it's different.
        """
        if PROPS[property_name] in wd_item.claims:
            return True
        else:
            return False

    def make_pywikibot_item(self, value, prop=None):
        val_item = None
        if type(value) is list and len(value) == 1:
            value = value[0]
        if utils.string_is_q_item(value):
            val_item = self.make_q_item(value)
        elif prop == PROPS["image"]:
            if self.item_has_prop("image", self.wd_item) is False:
                if utils.file_is_on_commons(value):
                    val_item = self.make_image_item(value)
        elif utils.tuple_is_coords(value) and prop == PROPS["coordinates"]:
            val_item = self.make_coords_item(value)
        elif isinstance(value, dict) and 'quantity_value' in value:
            val_item = self.make_quantity_item(value, self.repo)
        elif isinstance(value, dict) and 'time_value' in value:
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

    def add_claims(self, wd_item, claims, log):
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
                        if wd_claim is None:
                            continue
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
                            print("Adding value: ", prop, wd_value)
                            self.wdstuff.addNewClaim(
                                prop, wd_value, wd_item, ref)
                            if log:
                                t_id = wd_item.getID()
                                message = t_id + " ADDED CLAIM " + prop
                                log.logit(message)

    def create_new_item(self, log):
        item = self.wdstuff.make_new_item({}, summary=self.summary)
        if log:
            t_id = item.getID()
            message = t_id + " CREATE"
            log.logit(message)
        return item

    def upload(self):
        labels = self.make_labels()
        descriptions = self.make_descriptions()
        aliases = self.make_aliases()
        claims = self.data["statements"]
        self.add_labels(self.wd_item, labels, self.log)
        self.add_aliases(self.wd_item, aliases, self.log)
        self.add_descriptions(self.wd_item, descriptions, self.log)
        self.add_claims(self.wd_item, claims, self.log)

    def set_wd_item(self):
        item_exists = True if self.data["wd-item"] is not None else False
        if item_exists:
            # item_q = self.data["wd-item"]
            self.wd_item = self.wdstuff.QtoItemPage(self.TEST_ITEM)
            print(self.wd_item)
        else:
            self.wd_item = self.wdstuff.QtoItemPage(self.TEST_ITEM)
            # self.wd_item = self.create_new_item()

    def __init__(self, monument_object, log=None):
        self.log = False
        self.summary = "test"
        if log is not None:
            self.log = log
        self.data = monument_object.wd_item
        site = pywikibot.Site("wikidata", "wikidata")
        self.repo = site.data_repository()
        self.wdstuff = WDS(self.repo)
        self.set_wd_item()
