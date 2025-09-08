def get_info_models_query() -> str:
    return """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX modelldcatno: <https://data.norge.no/vocabulary/modelldcatno#>
PREFIX br: <https://raw.githubusercontent.com/Informasjonsforvaltning/organization-catalog/main/src/main/resources/ontology/organization-catalog.owl#>
SELECT DISTINCT ?record ?firstHarvested ?publisher ?orgId ?orgPath
WHERE { GRAPH ?g {
  ?informationmodel a modelldcatno:InformationModel .
  ?record foaf:primaryTopic ?informationmodel .
  ?record a dcat:CatalogRecord .
  ?record dct:issued ?firstHarvested .
  ?catalog modelldcatno:model ?informationmodel .
  OPTIONAL {
    ?informationmodel dct:publisher ?publisher .
    ?publisher dct:identifier ?orgId .
    ?publisher br:orgPath ?orgPath .
  }
}}"""
