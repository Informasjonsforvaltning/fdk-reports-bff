def get_concepts_query() -> str:
    return """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX br: <https://raw.githubusercontent.com/Informasjonsforvaltning/organization-catalog/main/src/main/resources/ontology/organization-catalog.owl#>
SELECT DISTINCT ?record ?firstHarvested ?publisher ?orgId ?orgPath
WHERE { GRAPH ?g {
  ?concept a skos:Concept .
  ?record foaf:primaryTopic ?concept .
  ?record a dcat:CatalogRecord .
  ?record dct:issued ?firstHarvested .
  ?collection skos:member ?concept .
  OPTIONAL {
    ?concept dct:publisher ?publisher .
    ?publisher dct:identifier ?orgId .
    ?publisher br:orgPath ?orgPath .
  }
}}"""
