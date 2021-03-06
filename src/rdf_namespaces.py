import abc

from src.utils import ContentKeys


class NamespaceProperty(metaclass=abc.ABCMeta):
    JSON_RDF = "json_rdf"
    TTL = "turtle"

    def __init__(self, syntax):
        self.syntax = syntax
        self.prefix = self.get_prefix()

    @abc.abstractmethod
    def get_prefix(self):
        pass

    @staticmethod
    def get_ttl_ns_definition():
        pass

    def get_property(self, from_value):
        return f"{self.prefix}{from_value}"


class RDF(NamespaceProperty):
    ttl_prefix = "rdf: "
    json_rdf_prefix = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

    def __init__(self, syntax):
        super().__init__(syntax)
        if self.syntax == NamespaceProperty.JSON_RDF:
            self.type = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        else:
            self.type = "a"

    def get_prefix(self) -> str:
        if self.syntax == NamespaceProperty.JSON_RDF:
            return RDF.json_rdf_prefix
        else:
            return self.ttl_prefix


class DCT(NamespaceProperty):
    ttl_prefix = "dct:"
    ttl_prefix_definition = "PREFIX dct: <http://purl.org/dc/terms/>"
    json_rdf_prefix = "http://purl.org/dc/terms/"

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
        self.license_document = self.get_property("LicenseDocument")
        self.isPartOf = self.get_property("isPartOf")
        self.title = self.get_property("title")

    @staticmethod
    def get_ttl_ns_definition():
        return "dct: <http://purl.org/dc/terms/>"

    def get_prefix(self) -> str:
        if self.syntax == NamespaceProperty.JSON_RDF:
            return DCT.json_rdf_prefix
        else:
            return DCT.ttl_prefix


class FOAF(NamespaceProperty):
    ttl_prefix = "foaf:"
    json_rdf_prefix = "http://xmlns.com/foaf/0.1/"

    def __init__(self, syntax):
        super().__init__(syntax)
        self.agent = self.get_property("Agent")
        self.name = self.get_property("name")
        self.primaryTopic = self.get_property("primaryTopic")

    def get_prefix(self) -> str:
        if self.syntax == NamespaceProperty.JSON_RDF:
            return FOAF.json_rdf_prefix
        else:
            return FOAF.ttl_prefix

    @staticmethod
    def get_ttl_ns_definition():
        return "foaf: <http://xmlns.com/foaf/0.1/>"


class OWL(NamespaceProperty):
    ttl_prefix = "owl:"
    json_rdf_prefix = "http://www.w3.org/2002/07/owl#"

    def __init__(self, syntax):
        super().__init__(syntax)
        self.sameAs = self.get_property("sameAs")

    def get_prefix(self):
        if self.syntax == NamespaceProperty.JSON_RDF:
            return OWL.json_rdf_prefix
        else:
            return OWL.ttl_prefix

    @staticmethod
    def get_ttl_ns_definition():
        return "owl: <http://www.w3.org/2002/07/owl%23>"


class DCAT(NamespaceProperty):
    ttl_prefix = "dcat:"
    json_rdf_prefix = "http://www.w3.org/ns/dcat#"

    def __init__(self, syntax):
        super().__init__(syntax)
        self.theme = self.get_property("theme")
        self.type_dataset = self.get_property("Dataset")
        self.dataset = self.get_property("dataset")
        self.distribution = self.get_property("distribution")
        self.distribution_type = self.get_property("Distribution")
        self.CatalogRecord = self.get_property("CatalogRecord")
        self.type_catalog = self.get_property("Catalog")
        self.type_service = self.get_property("service")
        self.mediaType = self.get_property("mediaType")

    def get_prefix(self):
        if self.syntax == NamespaceProperty.JSON_RDF:
            return DCAT.json_rdf_prefix
        else:
            return DCAT.ttl_prefix

    @staticmethod
    def get_ttl_ns_definition():
        return "dcat: <http://www.w3.org/ns/dcat%23>"


class XSD(NamespaceProperty):
    ttl_prefix = "xsd:"
    json_rdf_prefix = "http://www.w3.org/2001/XMLSchema#"

    def get_prefix(self):
        if self.syntax == NamespaceProperty.JSON_RDF:
            return XSD.json_rdf_prefix
        else:
            return XSD.ttl_prefix


class SKOS(NamespaceProperty):
    ttl_prefix = "skos:"
    json_rdf_prefix = "http://www.w3.org/2004/02/skos/core#"

    def __init__(self, syntax):
        super().__init__(syntax)
        self.concept = self.get_property("Concept")

    def get_prefix(self):
        if self.syntax == NamespaceProperty.JSON_RDF:
            return SKOS.json_rdf_prefix
        else:
            return SKOS.ttl_prefix


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


class JsonRDF:
    rdf = RDF(NamespaceProperty.JSON_RDF)
    dcat = DCAT(NamespaceProperty.JSON_RDF)
    dct = DCT(NamespaceProperty.JSON_RDF)
    foaf = FOAF(NamespaceProperty.JSON_RDF)
    owl = OWL(NamespaceProperty.JSON_RDF)
    xsd = XSD(NamespaceProperty.JSON_RDF)
    skos = SKOS(NamespaceProperty.JSON_RDF)

    @staticmethod
    def rdf_type_equals(rdf_property: str, entry) -> bool:
        try:
            if type(entry) is tuple:
                return entry[1][JsonRDF.rdf.type][0][ContentKeys.VALUE] == rdf_property
            else:
                return entry[JsonRDF.rdf.type][0][ContentKeys.VALUE] == rdf_property
        except KeyError:
            return False

    @staticmethod
    def rdf_type_in(rdf_property: str, entries: tuple) -> bool:
        for xsd_type in entries[1].items():
            if type(xsd_type[1]) == str:
                return False
            try:
                for rdf_type_property in xsd_type[1]:
                    if rdf_type_property[ContentKeys.VALUE] == rdf_property:
                        return True
            except KeyError:
                continue
        return True

    @staticmethod
    def node_rdf_property_equals(rdf_property: str, equals_value: str, entry) -> bool:
        values = entry[list(entry.keys())[0]]
        try:
            return values[rdf_property][0][ContentKeys.VALUE] == equals_value
        except KeyError:
            return False
        except TypeError:
            return False

    @staticmethod
    def node_uri_equals(node: dict, equals_value: str):
        node_uri = list(node.keys())[0]
        return node_uri == equals_value

    @staticmethod
    def node_uri_in(node: dict, compare_values: list):
        node_uri = list(node.keys())[0]
        return node_uri in compare_values
