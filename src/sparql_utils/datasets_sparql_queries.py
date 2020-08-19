from typing import List

from src.sparql_utils import ContentKeys
from src.sparql_utils.sparql_namespaces import DCT, FOAF, OWL, SparqlFunctionString, RDF, DCAT, XSD
from src.sparql_utils.sparql_query_builder import SparqlSelect, SparqlCount, SparqlWhere, SparqlGraphTerm, \
    SparqlFunction, SparqlBuilder, SparqlOptional, encode_for_sparql, SparqlFilter


def build_datasets_catalog_query(org_uris: List[str], theme: List[str]) -> str:
    prefixes = [DCT, FOAF, OWL]
    select_clause = SparqlSelect(variable_names=[ContentKeys.ORG_NAME, ContentKeys.ORGANIZATION_URI],
                                 count_variables=[SparqlCount(variable_name="item", as_name="count")]
                                 )
    where_clause = catalog_query_where_clause(org_uris, theme)

    query = SparqlBuilder(
        prefix=prefixes,
        select=select_clause,
        where=where_clause,
        group_by_str=f"?{ContentKeys.ORGANIZATION_URI} ?{ContentKeys.ORG_NAME}"
    ).build()
    return encode_for_sparql(query)


def catalog_query_where_clause(org_uris: List[str], theme: List[str]):
    bind_root = SparqlFunction(fun=SparqlFunctionString.BIND).str_with_inner_function("COALESCE(?sameAs, STR("
                                                                                      "?publisher)) AS ?organization")
    publisher_var = "publisher"
    publisher_a_foaf_a_agent = SparqlGraphTerm.build_graph_pattern(
        subject=SparqlGraphTerm(var="publisher"),
        predicate=SparqlGraphTerm(namespace_property=RDF.type),
        obj=SparqlGraphTerm(namespace_property=FOAF.agent),
        close_pattern_with="."
    )
    publisher_name_pattern = SparqlGraphTerm.build_graph_pattern(
        subject=SparqlGraphTerm(var=publisher_var),
        predicate=SparqlGraphTerm(namespace_property=FOAF.name),
        obj=SparqlGraphTerm(var=ContentKeys.ORG_NAME),
        close_pattern_with="."
    )

    graph_patterns = [
        publisher_a_foaf_a_agent,
        SparqlGraphTerm.build_graph_pattern(
            subject=SparqlGraphTerm(var="item"),
            predicate=SparqlGraphTerm(namespace_property=DCT.publisher),
            obj=SparqlGraphTerm(var=publisher_var),
            close_pattern_with="."
        ),
        publisher_name_pattern
    ]
    nested_select_clause = SparqlSelect(variable_names=["publisher", "organization"])
    nested_where = SparqlWhere(graphs=[publisher_a_foaf_a_agent],
                               functions=[bind_root],
                               optional=SparqlOptional(graphs=[
                                   SparqlGraphTerm.build_graph_pattern(
                                       subject=SparqlGraphTerm(var="publisher"),
                                       predicate=SparqlGraphTerm(namespace_property=OWL.sameAs),
                                       obj=SparqlGraphTerm(var="sameAs"),
                                       close_pattern_with="."
                                   )
                               ]),
                               filters=SparqlFilter.collect_filters(organization=org_uris)
                               )
    nested_builder = SparqlBuilder(select=nested_select_clause, where=nested_where)
    return SparqlWhere(graphs=graph_patterns, nested_clause=nested_builder)


def build_datasets_stats_query(org_uris: List[str], theme) -> str:
    return "PREFIX%20dcat:%20%3Chttp://www.w3.org/ns/dcat%23%3E%20PREFIX%20dct:%20%3Chttp://purl.org/dc/terms/%3E" \
           "%20PREFIX%20xsd:%20%3Chttp://www.w3.org/2001/XMLSchema%23%3E%20SELECT%20%28COUNT%28?d1%29%20AS%20" \
           "?withSubject%29%20%28COUNT%28?d2%29%20AS%20?opendata%29%20%28COUNT%28?d3%29%20AS%20?total%29%20%28COUNT" \
           "%28?d4%29%20AS%20?new_last_week%29%20%28COUNT%28?d5%29%20AS%20?nationalComponent%29%20WHERE%20{%20{" \
           "%20?d1%20a%20dcat:Dataset%20.%20FILTER%20EXISTS{%20?d1%20dct:subject%20?s%20.%20}%20}%20UNION%20{%20{" \
           "%20SELECT%20?d2%20%28GROUP_CONCAT%28DISTINCT%20?license%29%20AS%20?uris%29%20WHERE%20{" \
           "%20?d2%20a%20dcat:Dataset%20.%20?d2%20dct:accessRights%20?accessRights%20.%20?d2%20dcat:distribution%20" \
           "?distribution%20.%20?distribution%20dct:license%20?l%20.%20OPTIONAL%20{" \
           "%20?l%20dct:source%20?src%20.%20}%20BIND%28REPLACE%28STR%28?accessRights%29,%20%27^.%2A\\\\/%27," \
           "%20%27%27%29%20AS%20?publicCode%29%20BIND%28COALESCE%28?src," \
           "%20STR%28?l%29%29%20AS%20?license%29%20FILTER%20EXISTS{" \
           "%20?d2%20dct:accessRights%20?a%20.%20}%20FILTER%28?publicCode%20=%20%27PUBLIC%27%29%20FILTER%28STRLEN%28" \
           "?license%29%20%3E%200%29%20}%20GROUP%20BY%20?d2%20}%20}%20UNION%20{" \
           "%20?d3%20a%20dcat:Dataset%20.%20}%20UNION%20{" \
           "%20?d4%20a%20dcat:Dataset%20.%20?d4%20dct:issued%20?issued%20.%20FILTER%28?issued%20%3E=%20%28NOW%28%29" \
           "%20-%20%22P7D%22^^xsd:duration%29%29%20}%20UNION%20{" \
           "%20?d5%20a%20dcat:Dataset%20.%20?d5%20dct:provenance%20?provenance%20.%20FILTER%20CONTAINS%28LCASE%28STR" \
           "%28?provenance%29%29,%20%22nasjonal%22%29%20}%20} "


def build_datasets_access_rights_query(org_uris: List[str], theme) -> str:
    code_var = ContentKeys.ACCESS_RIGHTS_CODE
    prefixes = [DCT]
    select = SparqlSelect(variable_names=[code_var], count_variables=[SparqlCount(variable_name=code_var)])
    where_filters = SparqlFilter.collect_filters(organization=org_uris)
    var_dataset = "dataset"
    var_publisher = "publisher"
    var_organization = "organization"
    where_graphs = [
        SparqlGraphTerm.build_graph_pattern(
            subject=SparqlGraphTerm(var=var_dataset),
            predicate=SparqlGraphTerm(namespace_property=DCT.accessRights),
            obj=SparqlGraphTerm(var=code_var),
            close_pattern_with="."
        ),
    ]
    where_functions = None
    if where_filters:
        where_graphs.append(
            SparqlGraphTerm.build_graph_pattern(
                SparqlGraphTerm(var=var_dataset),
                SparqlGraphTerm(namespace_property=DCT.publisher),
                SparqlGraphTerm(var=var_publisher),
                close_pattern_with="."
            )
        )
        where_functions = [
            SparqlFunction(fun=SparqlFunctionString.STR, variable=var_publisher, as_name=var_organization,
                           parent=SparqlFunction(SparqlFunctionString.BIND))
        ]

    query = SparqlBuilder(
        prefix=prefixes,
        select=select,
        where=SparqlWhere(graphs=where_graphs,
                          functions=where_functions,
                          filters=where_filters
                          ),
        group_by_var=code_var
    ).build()
    return encode_for_sparql(query)


def build_datasets_formats_query(org_uris: List[str], theme) -> str:
    prefixes = [DCT]
    if org_uris:
        prefixes.append(DCAT)
    select = SparqlSelect(
        variable_names=[ContentKeys.FORMAT],
        count_variables=[(SparqlCount(variable_name=ContentKeys.FORMAT))]
    )
    var_distribution = "distribution"
    var_publisher = "publisher"
    var_org = "org"
    fun_bind = SparqlFunction(fun=SparqlFunctionString.BIND)
    fun_lcase_leaf = SparqlFunction(fun=SparqlFunctionString.LCASE, variable="distributionFormat", as_name="format",
                                    parent=fun_bind)
    fun_org_str_leaf = SparqlFunction(fun=SparqlFunctionString.STR, variable=var_publisher, as_name=var_org,
                                      parent=fun_bind)
    where_graphs = []
    if org_uris:
        where_graphs.append(
            SparqlGraphTerm.build_graph_pattern(
                SparqlGraphTerm(var="dataset"),
                SparqlGraphTerm(namespace_property=DCAT.distribution),
                SparqlGraphTerm(var=var_distribution),
                close_pattern_with="."
            )
        )
        where_graphs.append(
            SparqlGraphTerm.build_graph_pattern(
                SparqlGraphTerm(var="dataset"),
                SparqlGraphTerm(namespace_property=DCT.publisher),
                SparqlGraphTerm(var=var_publisher),
                close_pattern_with="."
            )
        )

    where_graphs.append(
        SparqlGraphTerm.build_graph_pattern(
            subject=SparqlGraphTerm(var=var_distribution),
            predicate=SparqlGraphTerm(namespace_property=DCT.format),
            obj=SparqlGraphTerm(var="distributionFormat"),
            close_pattern_with="."
        )
    )

    where_functions = [fun_lcase_leaf]
    if org_uris:
        where_functions.append(fun_org_str_leaf)
    where = SparqlWhere(graphs=where_graphs, functions=where_functions,
                        filters=SparqlFilter.collect_filters(org=org_uris))
    query = SparqlBuilder(prefix=prefixes, select=select, where=where, group_by_var="format").build()
    return encode_for_sparql(query)


def build_datasets_themes_query(org_uris: List[str], theme) -> str:
    prefixes = [DCAT]
    if org_uris:
        prefixes.append(DCT)
    select = SparqlSelect(
        variable_names=[ContentKeys.THEME],
        count_variables=[SparqlCount(variable_name=ContentKeys.THEME)]
    )
    var_dataset = "dataset"
    var_org = "org"
    var_publisher = "publisher"
    where_graphs = [
        SparqlGraphTerm.build_graph_pattern(
            subject=SparqlGraphTerm(var=var_dataset),
            predicate=SparqlGraphTerm(namespace_property=DCAT.theme),
            obj=SparqlGraphTerm(var=ContentKeys.THEME),
            close_pattern_with="."
        )
    ]

    if org_uris:
        where_graphs.append(
            SparqlGraphTerm.build_graph_pattern(
                subject=SparqlGraphTerm(var=var_dataset),
                predicate=SparqlGraphTerm(namespace_property=DCT.publisher),
                obj=SparqlGraphTerm(var=var_publisher)
            )
        )

    where_functions = None
    if org_uris:
        where_functions = [
            SparqlFunction(fun=SparqlFunctionString.STR, variable=var_publisher, as_name=var_org,
                           parent=SparqlFunction(fun=SparqlFunctionString.BIND))
        ]
    where = SparqlWhere(graphs=where_graphs,
                        filters=SparqlFilter.collect_filters(org=org_uris),
                        functions=where_functions)

    query = SparqlBuilder(prefix=prefixes, select=select, where=where, group_by_var=ContentKeys.THEME).build()
    return encode_for_sparql(query)


def build_dataset_time_series_query():
    base_var = "d"
    issued_var = "issued"
    prefixes = [DCT]
    select = SparqlSelect(
        variable_names=[ContentKeys.TIME_SERIES_MONTH, ContentKeys.TIME_SERIES_YEAR],
        count_variables=[SparqlCount(variable_name=base_var, as_name=ContentKeys.COUNT)]
    )
    where = SparqlWhere(graphs=[
        SparqlGraphTerm.build_graph_pattern(
            subject=SparqlGraphTerm(var=base_var),
            predicate=SparqlGraphTerm(namespace_property=DCT.issued),
            obj=SparqlGraphTerm(var=issued_var),
            close_pattern_with="."
        )
    ])

    month_fun = SparqlFunction(SparqlFunctionString.MONTH, variable=issued_var, as_name=ContentKeys.TIME_SERIES_MONTH)
    year_fun = SparqlFunction(SparqlFunctionString.YEAR, variable=issued_var, as_name=ContentKeys.TIME_SERIES_YEAR)
    group_by_str = f"({str(month_fun)}) ({str(year_fun)})"
    order_by = f"ASC(?{ContentKeys.TIME_SERIES_YEAR}) ASC(?{ContentKeys.TIME_SERIES_MONTH})"
    query = SparqlBuilder(prefix=prefixes,
                          select=select,
                          where=where,
                          group_by_str=group_by_str,
                          order_by_str=order_by).build()
    return encode_for_sparql(query)


def build_dataset_simple_statistic_query(field: ContentKeys, org_uris: [List[str]], theme):
    return simple_stat_functions[field](org_uris=org_uris, theme=theme)


def build_datasets_total_query(org_uris: [List[str]], theme):
    prefix = [DCAT, DCT]
    var_dataset = "dataaset"
    where_graphs = [
        SparqlGraphTerm.build_graph_pattern(
            subject=SparqlGraphTerm(var=var_dataset),
            predicate=SparqlGraphTerm(namespace_property=RDF.type),
            obj=SparqlGraphTerm(namespace_property=DCAT.dataset),
            close_pattern_with="."
        )
    ]
    select = SparqlSelect(count_variables=[SparqlCount(variable_name=var_dataset, as_name=ContentKeys.TOTAL)])
    where = SparqlWhere(graphs=where_graphs)
    query = SparqlBuilder(prefix=prefix, select=select, where=where).build()
    return encode_for_sparql(query)


def build_datasets_with_subject_query(org_uris: List[str], theme):
    prefix = [DCAT, DCT]
    var_dataset = "dataset"
    where_graphs = [
        SparqlGraphTerm.build_graph_pattern(
            subject=SparqlGraphTerm(var=var_dataset),
            predicate=SparqlGraphTerm(namespace_property=RDF.type),
            obj=SparqlGraphTerm(namespace_property=DCAT.dataset),
            close_pattern_with="."
        )
    ]
    filters = [SparqlFilter(filter_string="EXISTS {?dataset dct:subject ?subject .}")]
    select = SparqlSelect(count_variables=[SparqlCount(variable_name=var_dataset, as_name=ContentKeys.WITH_SUBJECT)])
    where = SparqlWhere(graphs=where_graphs, filters=filters)
    query = SparqlBuilder(prefix=prefix, select=select, where=where).build()
    return encode_for_sparql(query)


def build_dataset_open_data_query(org_uris: List[str], theme):
    # TODO: get reference data from
    # https://fellesdatakatalog.digdir.no/reference-data/codes/openlicenses
    # get public accessright from referenced data store

    open_licenses = ['http://data.norge.no/nlod/',
                     'http://data.norge.no/nlod/no/1.0',
                     'http://data.norge.no/nlod/no/2.0',
                     'http://creativecommons.org/licenses/by/4.0/',
                     'http://creativecommons.org/licenses/by/4.0/deed.no',
                     'http://creativecommons.org/publicdomain/zero/1.0/']

    public_access_right = '<http://publications.europa.eu/resource/authority/access-right/PUBLIC>'

    d_var = "d"
    access_right_var = "accessRights"
    dist_var = "distribution"
    dct_license_var = "l"
    license_source_var = "src"
    all_licenses_var = "license"
    prefix = [DCAT, DCT]
    select = SparqlSelect(
        count_variables=[SparqlCount(variable_name=d_var, as_name=ContentKeys.OPEN_DATA,
                                     inner_function=SparqlFunctionString.DISTINCT)]
    )
    where_graps = [
        build_var_a_dataset_graph(d_var),
        SparqlGraphTerm.build_graph_pattern(
            SparqlGraphTerm(var=d_var),
            SparqlGraphTerm(namespace_property=DCT.accessRights),
            SparqlGraphTerm(var=access_right_var),
            close_pattern_with="."
        ),
        SparqlGraphTerm.build_graph_pattern(
            SparqlGraphTerm(var=d_var),
            SparqlGraphTerm(namespace_property=DCAT.distribution),
            SparqlGraphTerm(var=dist_var),
            "."
        ),
        SparqlGraphTerm.build_graph_pattern(
            SparqlGraphTerm(var=dist_var),
            SparqlGraphTerm(namespace_property=DCT.license),
            SparqlGraphTerm(var=dct_license_var),
            "."
        )
    ]

    optional = SparqlOptional(
        graphs=[
            SparqlGraphTerm.build_graph_pattern(
                SparqlGraphTerm(var=dct_license_var),
                SparqlGraphTerm(namespace_property=DCT.source),
                SparqlGraphTerm(var=license_source_var),
                "."
            )

        ]
    )
    combine_licenses_function = SparqlFunction(
        fun=SparqlFunctionString.BIND).str_with_inner_function(f"COALESCE(?{license_source_var}, STR(?{dct_license_var})) AS ?{all_licenses_var}")

    filters = SparqlFilter.collect_filters(license=open_licenses)
    filters.append(
        SparqlFilter(filter_string=f"?{access_right_var}={public_access_right}")
    )

    where = SparqlWhere(
        graphs=where_graps,
        functions=[combine_licenses_function],
        optional=optional,
        filters=filters
    )

    query = SparqlBuilder(
        prefix=prefix,
        select=select,
        where=where
    ).build()
    return encode_for_sparql(query)


def build_datasets_new_last_week_query(org_uris: List[str], theme) -> str:
    prefix = [DCT, XSD]
    d_var = "d"
    issued_var = "issued"
    select = SparqlSelect(count_variables=[SparqlCount(variable_name=d_var, as_name=ContentKeys.NEW_LAST_WEEK)])
    where_graphs = [
        SparqlGraphTerm.build_graph_pattern(
            SparqlGraphTerm(var=d_var),
            SparqlGraphTerm(namespace_property=DCT.issued),
            SparqlGraphTerm(var=issued_var)
        )
    ]
    filters = [SparqlFilter(filter_string='?issued >= (NOW() - "P7D"^^xsd:duration ) ')]
    where = SparqlWhere(
        graphs=where_graphs,
        filters=filters
    )

    query = SparqlBuilder(
        prefix=prefix,
        select=select,
        where=where
    ).build()
    return encode_for_sparql(query)


def build_datasets_national_component_query(org_uris: List[str], theme) -> str:
    d_var = "d"
    provenance_var = "provenance"
    national_provenance_uri = "<http://data.brreg.no/datakatalog/provinens/nasjonal>"
    prefix = [DCT, DCAT]
    select = SparqlSelect(count_variables=[SparqlCount(variable_name=d_var, as_name=ContentKeys.NATIONAL_COMPONENT)])
    a_dataset_pattern = build_var_a_dataset_graph(d_var)
    where_graphs = [
        a_dataset_pattern,
        SparqlGraphTerm.build_graph_pattern(
            SparqlGraphTerm(var=d_var),
            SparqlGraphTerm(namespace_property=DCT.provenance),
            SparqlGraphTerm(var=provenance_var)
        )
    ]

    filters = [
        SparqlFilter(filter_string=f"?{provenance_var}={national_provenance_uri}")
    ]

    where = SparqlWhere(
        graphs=where_graphs,
        filters=filters
    )

    query = SparqlBuilder(
        prefix=prefix,
        select=select,
        where=where
    ).build()
    return encode_for_sparql(query)


simple_stat_functions = {
    ContentKeys.TOTAL: build_datasets_total_query,
    ContentKeys.OPEN_DATA: build_dataset_open_data_query,
    ContentKeys.NATIONAL_COMPONENT: build_datasets_national_component_query,
    ContentKeys.WITH_SUBJECT: build_datasets_with_subject_query,
    ContentKeys.NEW_LAST_WEEK: build_datasets_new_last_week_query
}


def build_var_a_dataset_graph(var: str):
    return SparqlGraphTerm.build_graph_pattern(
            subject=SparqlGraphTerm(var=var),
            predicate=SparqlGraphTerm(namespace_property=RDF.type),
            obj=SparqlGraphTerm(namespace_property=DCAT.dataset),
            close_pattern_with="."
        )

