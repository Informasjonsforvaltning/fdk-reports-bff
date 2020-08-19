from typing import List

from src.sparql_utils import ContentKeys
from src.sparql_utils.sparql_namespaces import DCT, FOAF, OWL, SparqlFunctionString, RDF, DCAT
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
    breakpoint()
    return encode_for_sparql(query)


def build_datasets_themes_query(orgpath, theme) -> str:
    prefixes = [DCAT]
    select = SparqlSelect(
        variable_names=[ContentKeys.THEME],
        count_variables=[SparqlCount(variable_name=ContentKeys.THEME)]
    )
    where = SparqlWhere(graphs=[
        SparqlGraphTerm.build_graph_pattern(
            subject=SparqlGraphTerm(var="dataset"),
            predicate=SparqlGraphTerm(namespace_property=DCAT.theme),
            obj=SparqlGraphTerm(var=ContentKeys.THEME),
            close_pattern_with="."
        )
    ])

    query = SparqlBuilder(prefix=prefixes, select=select, where=where, group_by_var=ContentKeys.THEME).build()
    return encode_for_sparql(query)


def build_dataset_time_series_query():
    base_var = "d"
    issued_var = "issued"
    prefixes = [DCAT, DCT]
    select = SparqlSelect(
        variable_names=[ContentKeys.TIME_SERIES_MONTH, ContentKeys.TIME_SERIES_YEAR],
        count_variables=[SparqlCount(variable_name=base_var, as_name=ContentKeys.COUNT)]
    )
    where = SparqlWhere(graphs=[
        SparqlGraphTerm.build_graph_pattern(
            subject=SparqlGraphTerm(var=base_var),
            predicate=SparqlGraphTerm(namespace_property=RDF.type),
            obj=SparqlGraphTerm(namespace_property=DCAT.dataset),
            close_pattern_with="."
        ),
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
