"""
    def make_labels(self):
        labels = self.wd_item["labels"]
        new_labels = {}
        for item in labels:
            new_labels[item] = {'language':item, 'value':labels[item]}
        return new_labels

    def make_descriptions(self):
        descriptions = self.wd_item["descriptions"]
        new_descriptions = {}
        for item in descriptions:
            new_descriptions[item] = {'language':item, 'value':descriptions[item]}
        return new_descriptions

    def create_new_item(self):
        repo = pywikibot.Site("test", "wikidata").data_repository()
        wdstuff = WDS(repo)
        data = {'labels':{}, 'descriptions':{}}
        data["labels"] = self.make_labels()
        data["descriptions"] = self.make_descriptions()
        summary = "creating new item.. " + self.name
        monument_item = None
        monument_item = wdstuff.make_new_item(data, summary)
        print("creating new item...")


    def upload(self):
        statements = self.wd_item["statements"]
        labels = self.wd_item["labels"]
        descriptions = self.wd_item["descriptions"]
        exists = True if self.wd_item["wd-item"] is not None else False
        if exists:
            print("item exists: " + self.wd_item["wd-item"])
            test_item = "Q4115189"
            site = pywikibot.Site("wikidata", "wikidata")
            repo = site.data_repository()
            wdstuff = WDS(repo)
            item = pywikibot.ItemPage(repo, test_item)
            item_dict = item.get()
            clm_dict = item_dict["claims"]
            print(statements)
            print(clm_dict)
            for prop in statements:
                if prop not in clm_dict:
                    print(prop)
                    val = statements[prop][0]["value"]
                    if str(val).startswith("Q"):
                        val_item = wdstuff.QtoItemPage(val)
                        statement = wdstuff.Statement(val_item)
                        print(statement)
                        test_item_page = wdstuff.QtoItemPage(test_item)
                        test_item_page.get()
                        wdstuff.addNewClaim(prop, statement, test_item_page, None)
        else:
            pass
            #new_item = self.create_new_item()

"""
class Uploader(object):
    def __init__(self, monument_object):
        monument_data = monument_object.wd_item
        print(monument_data)

    def upload(self):
        print("uploading....")