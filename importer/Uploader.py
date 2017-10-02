from wikidataStuff.WikidataStuff import WikidataStuff as WDS
import pywikibot
import importer_utils as utils
from os import path
import sys

MAPPING_DIR = "mappings"
PROPS = utils.load_json(path.join(MAPPING_DIR, "props_general.json"))
P31_BLACKLIST = utils.load_json(path.join(MAPPING_DIR, "P31_blacklist.json"))


class Uploader(object):

    TEST_ITEM = "Q4115189"

    def add_labels(self, target_item, labels, log):
        """Add labels and aliases."""
        self.wdstuff.add_multiple_label_or_alias(labels, target_item)
        if log:
            t_id = target_item.getID()
            message = "{} ADDED LABELS {}".format(t_id, labels)
            log.logit(message)

    def add_descriptions(self, target_item, descriptions, log):
        """Add descriptions."""
        self.wdstuff.add_multiple_descriptions(descriptions, target_item)
        if log:
            t_id = target_item.getID()
            message = "{} ADDED DESCRIPTIONS {}".format(t_id, descriptions)
            log.logit(message)

    def make_image_item(self, filename):
        commonssite = utils.create_site_instance("commons", "commons")
        imagelink = pywikibot.Link(
            filename, source=commonssite, defaultNamespace=6)
        return pywikibot.FilePage(imagelink)

    def make_coords_item(self, coordstuple):
        """
        Create a Coordinate item.

        Default precision, such as used by
        http://pywikibot.readthedocs.io/en/latest/_modules/scripts/claimit/
        """
        DEFAULT_PREC = 0.0001
        return pywikibot.Coordinate(
            coordstuple[0], coordstuple[1], precision=DEFAULT_PREC)

    def make_quantity_item(self, quantity, repo):
        """
        Create claim for a quantity, with optional unit.

        quantity: {'unit': 'Q11573', 'quantity_value': 6.85}
        """
        value = quantity['quantity_value']
        if 'unit' in quantity:
            unit = self.make_q_item(quantity['unit'])
        else:
            unit = None
        return pywikibot.WbQuantity(amount=value, unit=unit, site=repo)

    def make_monolingual_item(self, quantity, repo):
        """
        Create claim for a monolingual text.

        quantity: {'monolingual_value': 'The bestest text', 'lang': 'en'}
        """
        return pywikibot.WbMonolingualText(
            text=quantity['monolingual_value'], language=quantity['lang'])

    def make_time_item(self, quantity, repo):
        """
        Create a WbTime item.

        quantity: {'time_value': <dict>}
        with <dict> per utils.datetime_object_to_dict

        This only works for full years and dates.
        @TODO: Make it work for year range!
        """
        value = quantity['time_value']
        return pywikibot.WbTime(**value)

    def make_q_item(self, q_number):
        """Create a regular Item, if target is not a disambiguation."""
        q_item = None
        disambiguation_page = "Q4167410"
        instances = utils.get_P31(q_number, self.repo)
        q_item = self.wdstuff.QtoItemPage(q_number)

        if (disambiguation_page in instances or
           (self.wd_item_q and self.wd_item_q == q_item)):
            mes = "{} cannot be added to {} as target of claim. Exiting."
            sys.exit(mes.format(q_item, self.wd_item_q))
        else:
            return q_item

    def item_has_prop(self, property_name, wd_item):
        """
        Check if item has a specific property.

        This is different from WikidataStuff has_claim()
        because it checks whether the property exists,
        not if the statement matches.
        If the target item already uses the property,
        a new claim will not be added even if it's different.
        """
        pid = PROPS.get(property_name)
        if utils.string_is_p_item(property_name):
            pid = property_name

        if pid and pid in wd_item.claims:
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
            if not self.item_has_prop("image", self.wd_item) and \
                    utils.file_is_on_commons(value):
                val_item = self.make_image_item(value)
        elif utils.tuple_is_coords(value) and prop == PROPS["coordinates"]:
            # Don't upload coords if item already has one.
            # Temp. until https://phabricator.wikimedia.org/T160282 is solved.
            if not self.item_has_prop("coordinates", self.wd_item):
                val_item = self.make_coords_item(value)
        elif isinstance(value, dict) and 'quantity_value' in value:
            val_item = self.make_quantity_item(value, self.repo)
        elif isinstance(value, dict) and 'time_value' in value:
            val_item = self.make_time_item(value, self.repo)
        elif isinstance(value, dict) and 'monolingual_value' in value:
            val_item = self.make_monolingual_item(value)
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

    def make_stated_in_reference(self, ref_dict):
        prop = ref_dict["source"]["prop"]
        prop_date = ref_dict["published"]["prop"]
        date = ref_dict["published"]["value"]
        date_item = pywikibot.WbTime(**date)
        source_item = self.wdstuff.QtoItemPage(ref_dict["source"]["value"])
        source_claim = self.wdstuff.make_simple_claim(prop, source_item)
        if "reference_url" in ref_dict:
            ref_url = ref_dict["reference_url"]["value"]
            ref_url_prop = ref_dict["reference_url"]["prop"]
            ref_url_claim = self.wdstuff.make_simple_claim(
                ref_url_prop, ref_url)
            ref = self.wdstuff.Reference(
                source_test=[source_claim, ref_url_claim],
                source_notest=self.wdstuff.make_simple_claim(prop_date, date_item))
        else:
            ref = self.wdstuff.Reference(
                source_test=[source_claim],
                source_notest=self.wdstuff.make_simple_claim(prop_date, date_item))
        return ref

    def add_claims(self, wd_item, claims, log):
        if wd_item:
            for claim in claims:
                prop = claim
                for x in claims[claim]:
                    if (x.get("if_empty") and
                            self.item_has_prop(prop, wd_item)):
                        continue

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
                        for ref in refs:
                            # This only works if it's a url.
                            # If we have references of different sort,
                            # this will have to be appended.
                            if utils.is_valid_url(ref):
                                ref = self.make_url_reference(ref)
                            else:
                                ref = self.make_stated_in_reference(ref)
                        if wd_value:
                            self.wdstuff.addNewClaim(
                                prop, wd_value, wd_item, ref)
                            if log:
                                t_id = wd_item.getID()
                                message = "{} ADDED CLAIM {}".format(
                                    t_id, prop)
                                log.logit(message)

    def create_new_item(self, log):
        item = self.wdstuff.make_new_item({}, self.summary)
        if log:
            t_id = item.getID()
            message = "{} CREATE".format(t_id)
            log.logit(message)
        return item

    def get_username(self):
        """Get Wikidata login that will be used to upload."""
        return pywikibot.config.usernames["wikidata"]["wikidata"]

    def upload(self):
        if self.data["upload"] is False:
            print("SKIPPING ITEM")
            return
        claims = self.data["statements"]
        labels = self.data["labels"]
        descriptions = self.data["descriptions"]
        self.add_labels(self.wd_item, labels, self.log)
        self.add_descriptions(self.wd_item, descriptions, self.log)
        self.add_claims(self.wd_item, claims, self.log)

    def set_wd_item(self):
        """
        Determine WD item to manipulate.

        In live mode, if data object has associated WD item,
        check whether it doesn't have a disallowed P31,
        and if it doesn't edit it. Otherwise, create a new WD item.
        In sandbox mode, all edits are done on the WD Sandbox item.
        """
        if self.live:
            if self.data["wd-item"] is None:
                self.wd_item = self.create_new_item(self.log)
                self.wd_item_q = self.wd_item.getID()
            else:
                disallowed = [x["item"] for x in P31_BLACKLIST]
                item_q = self.data["wd-item"]
                if utils.is_blacklisted_P31(item_q, self.repo, disallowed):
                    if self.log:
                        message = "{} -- SET AS WD-ITEM BUT POSSIBLY WRONG AND THUS REMOVED".format(item_q)
                        self.log.logit(message)
                    self.wd_item = self.create_new_item(self.log)
                    self.wd_item_q = self.wd_item.getID()
                else:
                    self.wd_item = self.wdstuff.QtoItemPage(item_q)
                    self.wd_item_q = item_q
        else:
            self.wd_item = self.wdstuff.QtoItemPage(self.TEST_ITEM)
            self.wd_item_q = self.TEST_ITEM

    def __init__(self,
                 monument_object,
                 repo,
                 log=None,
                 tablename=None,
                 live=False):
        """
        Initialize an Upload object for a single Monument.

        :param monument_object: Dictionary of Monument data
        :param repo: Data repository of site to work on (Wikidata)
        :param log: Enable logging to file
        :param tablename: Name of db table, used in edit summary
        :param live: Whether to work on real WD items or in the sandbox
        """
        self.repo = repo
        self.log = False
        self.summary = "#COH #WLM #{}".format(tablename)
        self.live = live
        print("User: {}".format(self.get_username()))
        print("Edit summary: {}".format(self.summary))
        if self.live:
            print("LIVE MODE")
        else:
            print("SANDBOX MODE: {}".format(self.TEST_ITEM))
        print("---------------")
        if log is not None:
            self.log = log
        self.data = monument_object.wd_item
        self.wdstuff = WDS(self.repo, edit_summary=self.summary, no_wdss=True)
        self.set_wd_item()
