from Monument import Monument


class RoRo(Monument):

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("ro", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
