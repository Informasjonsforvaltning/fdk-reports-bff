import abc


class NamespaceProperty(metaclass=abc.ABCMeta):
    JSON_LD = "json_ld"
    TTL = "turtle"

    def __init__(self, syntax):
        self.syntax = syntax
        self.prefix = self.get_prefix()

    @abc.abstractmethod
    def get_prefix(self):
        pass

    def get_property(self, from_value):
        return f"{self.prefix}{from_value}"


class RDF(NamespaceProperty):
    ttl_prefix = "rdf: "
    json_ld_prefix = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

    def __init__(self, syntax):
        super().__init__(syntax)
        self.type = self.get_property("type")

    def get_prefix(self) -> str:
        if self.syntax == NamespaceProperty.JSON_LD:
            return RDF.json_ld_prefix


class DCT(NamespaceProperty):
    ttl_prefix = "dct:"
    ttl_prefix_definition = "PREFIX dct: <http://purl.org/dc/terms/>"
    json_ld_prefix = "http://purl.org/dc/terms/"

    def __init__(self, syntax):
        super().__init__(syntax)
        self.format = self.get_property("format")
        self.issued = self.get_property("issued")
        self.publisher = self.get_property("publisher")
        self.accessRights = self.get_property("accessRights")
        self.provenance = self.get_property("provenance")
        self.license = self.get_property("license")
        self.source = self.get_property("source")
        self.subject = self.get_property("subject")

    def get_prefix(self) -> str:
        if self.syntax == NamespaceProperty.JSON_LD:
            return DCT.json_ld_prefix
        else:
            return DCT.ttl_prefix


class FOAF(NamespaceProperty):
    ttl_prefix = "foaf:"
    json_ld_prefix = "http://xmlns.com/foaf/0.1/"

    def __init__(self, syntax):
        super().__init__(syntax)
        self.agent = self.get_property("Agent")
        self.name = self.get_property("name")
        self.primaryTopic = self.get_property("primaryTopic")

    def get_prefix(self) -> str:
        if self.syntax == NamespaceProperty.JSON_LD:
            return FOAF.json_ld_prefix
        else:
            return FOAF.ttl_prefix


class OWL(NamespaceProperty):
    ttl_prefix = "owl:"
    json_ld_prefix = "http://www.w3.org/2002/07/owl#"

    def __init__(self, syntax):
        super().__init__(syntax)
        self.sameAs = self.get_property("sameAs")

    def get_prefix(self):
        if self.syntax == NamespaceProperty.JSON_LD:
            return OWL.json_ld_prefix
        else:
            return OWL.ttl_prefix


class DCAT(NamespaceProperty):
    ttl_prefix = "dcat:"
    json_ld_prefix = "http://www.w3.org/ns/dcat#"

    def __init__(self, syntax):
        super().__init__(syntax)
        self.theme = self.get_property("theme")
        self.dataset = self.get_property("Dataset")
        self.distribution = self.get_property("distribution")

    def get_prefix(self):
        if self.syntax == NamespaceProperty.JSON_LD:
            return DCAT.json_ld_prefix
        else:
            return DCAT.ttl_prefix


class XSD(NamespaceProperty):
    ttl_prefix = "xsd:"
    json_ld_prefix = "http://www.w3.org/2001/XMLSchema#"

    def get_prefix(self):
        if self.syntax == NamespaceProperty.JSON_LD:
            return XSD.json_ld_prefix
        else:
            return XSD.ttl_prefix


class SparqlFunctionString:
    DISTINCT = "DISTINCT"
    YEAR = "YEAR"
    MONTH = "MONTH"
    STR = "STR"
    REPLACE = "REPLACE"
    BIND = "BIND"
    LCASE = "LCASE"
    COUNT = "COUNT"
    COALESCE = "COALESCE"


class ContentKeys:
    SRC_ORGANIZATION = "publisher"
    FORMAT = "format"
    WITH_SUBJECT = "withSubject"
    OPEN_DATA = "opendata"
    TOTAL = "total"
    NEW_LAST_WEEK = "new_last_week"
    NATIONAL_COMPONENT = "nationalComponent"
    ORGANIZATION = "organization"
    COUNT = "count"
    VALUE = "value"
    ACCESS_RIGHTS_CODE = "code"
    TIME_SERIES_MONTH = "month"
    TIME_SERIES_YEAR = "year"
    TIME_SERIES_Y_AXIS = "yAxis"
    TIME_SERIES_X_AXIS = "xAxis"
    THEME = "theme"
    ORG_NAME = "name"
    ORGANIZATION_URI = "organization"


class OrgCatalogKeys:
    NAME = "name"
    URI = "norwegianRegistry"
    ORG_PATH = "orgPath"


class JSON_LD:
    RDF = RDF(NamespaceProperty.JSON_LD)
    DCAT = DCAT(NamespaceProperty.JSON_LD)
    DCT = DCT(NamespaceProperty.JSON_LD)
    FOAF = FOAF(NamespaceProperty.JSON_LD)
    OWL = OWL(NamespaceProperty.JSON_LD)
    XSD = XSD(NamespaceProperty.JSON_LD)

    @staticmethod
    def rdf_type_equals(rdf_property: str, entry) -> bool:
        try:
            if type(entry) is tuple:
                return entry[1][JSON_LD.RDF.type][0][ContentKeys.VALUE] == rdf_property
            else:
                return entry[JSON_LD.RDF.type][0][ContentKeys.VALUE] == rdf_property
        except KeyError:
            return False

    @staticmethod
    def node_rdf_property_equals(rdf_property: str, equals_value: str, entry) -> bool:
        values = entry[list(entry.keys())[0]]
        try:
            return values[rdf_property][0][ContentKeys.VALUE] == equals_value
        except KeyError:
            return False

    @staticmethod
    def node_uri_equals(node: dict, equals_value: str):
        node_uri = list(node.keys())[0]
        return node_uri == equals_value

    @staticmethod
    def node_uri_in(node: dict, compare_values: list):
        node_uri = list(node.keys())[0]
        return node_uri in compare_values
