def get_datasets_query() -> str:
    return """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX fdk: <https://raw.githubusercontent.com/Informasjonsforvaltning/fdk-reasoning-service/main/src/main/resources/ontology/fdk.owl#>
PREFIX br: <https://raw.githubusercontent.com/Informasjonsforvaltning/organization-catalog/main/src/main/resources/ontology/organization-catalog.owl#>
SELECT DISTINCT ?dataset ?record ?theme ?accessRights ?provenance ?subject ?isOpenData ?transportportal
WHERE { GRAPH ?g {
  ?dataset a dcat:Dataset .
  ?record foaf:primaryTopic ?dataset .
  ?record a dcat:CatalogRecord .

  OPTIONAL { ?dataset dcat:theme ?theme . }
  OPTIONAL { ?dataset dct:accessRights ?accessRights . }
  OPTIONAL { ?dataset dct:provenance ?provenance . }
  OPTIONAL { ?dataset dct:subject ?subject . }
  OPTIONAL { ?dataset fdk:isOpenData ?isOpenData . }
  OPTIONAL { ?dataset fdk:isRelatedToTransportportal ?transportportal . }
}}"""


def get_dataset_catalogs_query() -> str:
    return """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX fdk: <https://raw.githubusercontent.com/Informasjonsforvaltning/fdk-reasoning-service/main/src/main/resources/ontology/fdk.owl#>
PREFIX br: <https://raw.githubusercontent.com/Informasjonsforvaltning/organization-catalog/main/src/main/resources/ontology/organization-catalog.owl#>
SELECT DISTINCT ?dataset ?record ?catalog ?catalogTitle
WHERE { GRAPH ?g {
  ?dataset a dcat:Dataset .
  ?record foaf:primaryTopic ?dataset .
  ?record a dcat:CatalogRecord .

  ?record dct:isPartOf ?catalogRecord .
  ?catalogRecord foaf:primaryTopic ?catalog .
  OPTIONAL { ?catalog dct:title ?catalogTitle . }
}}"""


def get_dataset_distributions_query() -> str:
    return """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX fdk: <https://raw.githubusercontent.com/Informasjonsforvaltning/fdk-reasoning-service/main/src/main/resources/ontology/fdk.owl#>
PREFIX br: <https://raw.githubusercontent.com/Informasjonsforvaltning/organization-catalog/main/src/main/resources/ontology/organization-catalog.owl#>
SELECT DISTINCT ?dataset ?record ?mediaType ?format
WHERE { GRAPH ?g {
  ?dataset a dcat:Dataset .
  ?record foaf:primaryTopic ?dataset .
  ?record a dcat:CatalogRecord .

  ?dataset dcat:distribution ?distribution .
  OPTIONAL { ?distribution dcat:mediaType ?mediaType . }
  OPTIONAL { ?distribution dct:format ?format . }
}}"""


def get_dataset_publishers_query() -> str:
    return """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX fdk: <https://raw.githubusercontent.com/Informasjonsforvaltning/fdk-reasoning-service/main/src/main/resources/ontology/fdk.owl#>
PREFIX br: <https://raw.githubusercontent.com/Informasjonsforvaltning/organization-catalog/main/src/main/resources/ontology/organization-catalog.owl#>
SELECT DISTINCT ?dataset ?record ?publisher ?orgId ?orgPath
WHERE { GRAPH ?g {
  ?dataset a dcat:Dataset .
  ?record foaf:primaryTopic ?dataset .
  ?record a dcat:CatalogRecord .

  ?dataset dct:publisher ?publisher .
  OPTIONAL { ?publisher dct:identifier ?orgId . }
  OPTIONAL { ?publisher br:orgPath ?orgPath . }
}}"""
