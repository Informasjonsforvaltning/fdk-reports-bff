from datetime import datetime
from typing import List, Optional

from fdk_reports_bff.elasticsearch.queries import EsMappings
from fdk_reports_bff.utils import ParsedDataPoint, ThemeProfile


class Response:
    def __init__(
        self: any,
        total_objects: int,
        organization_count: int,
        new_last_week: int,
        catalogs: List[dict],
        org_paths: List[dict],
    ) -> any:
        self.totalObjects = total_objects
        self.newLastWeek = new_last_week
        self.catalogs = catalogs or []
        self.orgPaths = org_paths or []
        self.organizationCount = organization_count

    def populate_from_es(self: any, es_result: dict) -> "Response":
        self.totalObjects = es_result["page"]["totalElements"]
        harvest_aggs = es_result["aggregations"]["firstHarvested"]["buckets"]
        self.newLastWeek = [
            x["count"] for x in harvest_aggs if x["key"] == "last7days"
        ][0]
        self.catalogs = es_result["aggregations"]["orgPath"]["buckets"]


class InformationModelResponse(Response):
    def __init__(
        self: any,
        total_objects: int = None,
        new_last_week: int = None,
        catalogs: List[dict] = None,
        org_paths: List[dict] = None,
        organization_count: int = 0,
    ) -> any:
        super().__init__(
            total_objects, organization_count, new_last_week, catalogs, org_paths
        )

    @staticmethod
    def from_es(es_result: dict) -> any:
        response = InformationModelResponse()
        response.populate_from_es(es_result=es_result)
        return response

    def json(self: any) -> dict:
        serialized = self.__dict__
        return serialized

    @staticmethod
    def empty_response() -> any:
        return InformationModelResponse(
            total_objects=0, new_last_week=0, catalogs=None, org_paths=None
        )


class DataServiceResponse(Response):
    def __init__(
        self: any,
        total_objects: int = None,
        new_last_week: int = None,
        catalogs: List[dict] = None,
        org_paths: List[dict] = None,
        organization_count: int = 0,
        media_types: List[dict] = None,
    ) -> any:
        super().__init__(
            total_objects, organization_count, new_last_week, catalogs, org_paths
        )
        self.formats = media_types or []

    @staticmethod
    def from_es(es_result: dict) -> any:
        response = DataServiceResponse()
        response.populate_from_es(es_result=es_result)
        return response

    def json(self: any) -> dict:
        serialized = self.__dict__
        return serialized

    @staticmethod
    def empty_response() -> any:
        return DataServiceResponse(
            total_objects=0, new_last_week=0, catalogs=None, org_paths=None
        )


class ConceptResponse(Response):
    def __init__(
        self: any,
        total_objects: int = 0,
        new_last_week: int = None,
        catalogs: list = None,
        most_in_use: list = None,
        org_paths: list = None,
        organization_count: int = 0,
    ) -> any:
        super().__init__(
            total_objects, organization_count, new_last_week, catalogs, org_paths
        )
        if most_in_use:
            self.mostInUse = most_in_use

    @staticmethod
    def from_es(es_result: dict, most_in_use: dict) -> any:
        response = ConceptResponse()
        response.populate_from_es(es_result=es_result)
        response.mostInUse = ConceptResponse.parse_reference_list(most_in_use)
        return response

    @staticmethod
    def parse_reference_list(result_from_harvester: dict) -> list:
        concepts = result_from_harvester["_embedded"]["concepts"]
        reference_list = []
        for concept in concepts:
            ref = {"prefLabel": concept["prefLabel"], "uri": concept["uri"]}
            reference_list.append(ref)
        return reference_list

    def json(self: any) -> any:
        serialized = self.__dict__
        return serialized

    @staticmethod
    def empty_response() -> any:
        return ConceptResponse(
            total_objects=0,
            new_last_week=0,
            catalogs=None,
            most_in_use=None,
            org_paths=None,
            organization_count=0,
        )


class DataSetResponse(Response):
    def __init__(
        self: any,
        dist_formats: List[dict],
        total: str,
        organization_count: int,
        new_last_week: str,
        opendata: str,
        national_component: str,
        with_subject: str,
        catalogs: List[dict],
        org_paths: List[dict],
        themes: List[dict],
        access_rights: List[dict],
        theme_profile: Optional[ThemeProfile] = None,
    ) -> any:
        super().__init__(
            total_objects=total,
            new_last_week=new_last_week,
            catalogs=catalogs,
            org_paths=org_paths,
            organization_count=organization_count,
        )

        self.opendata = opendata
        self.nationalComponent = national_component
        self.withSubject = with_subject
        self.themesAndTopicsCount = themes or []
        self.formats = dist_formats or []
        self.accessRights = access_rights or []
        if theme_profile is not None:
            self.customize_for_theme_profile(theme_profile)

    def customize_for_theme_profile(self: any, theme_profile: ThemeProfile) -> None:
        if theme_profile == ThemeProfile.TRANSPORT:
            theme_profile_themes = [
                theme
                for theme in self.themesAndTopicsCount
                if theme.get("key") in ThemeProfile.TRANSPORT_THEMES
            ]
            self.themesAndTopicsCount = theme_profile_themes

    def json(self: any) -> dict:
        serialized = self.__dict__
        return serialized

    @staticmethod
    def empty_response() -> None:
        return DataSetResponse(
            dist_formats=None,
            total="0",
            new_last_week="0",
            opendata="0",
            national_component="0",
            with_subject="0",
            catalogs=None,
            themes=None,
            access_rights=None,
        )


class TimeSeriesResponse:
    def __init__(self: any, es_time_series: List[dict]) -> any:
        self.time_series = []
        self.last_data_point: ParsedDataPoint = None
        self.parse_es_time_series(es_time_series=es_time_series)
        self.add_months_from_last_data_point_to_now()

    def parse_es_time_series(self: any, es_time_series: dict) -> None:
        last_count = 0
        time_buckets = es_time_series[EsMappings.AGGREGATIONS][EsMappings.TIME_SERIES][
            EsMappings.BUCKETS
        ]
        for time_bucket in time_buckets:
            new_data_point = ParsedDataPoint(
                es_bucket=time_bucket, last_month_count=last_count
            )
            last_count = new_data_point.y_axis
            self.add(new_data_point)

    def add(self: any, parsed_entry: any) -> None:
        if len(self.time_series) == 0:
            self.time_series.append(parsed_entry.response_dict())
            self.last_data_point = parsed_entry
        elif parsed_entry == self.last_data_point.get_next_month():
            self.time_series.append(parsed_entry.response_dict())
            self.last_data_point = parsed_entry
        else:
            while self.last_data_point.get_next_month() != parsed_entry:
                next_month = self.last_data_point.get_next_month()
                self.time_series.append(next_month.response_dict())
                self.last_data_point = next_month
            self.time_series.append(parsed_entry.response_dict())
            self.last_data_point = parsed_entry

    def add_months_from_last_data_point_to_now(self: any) -> None:
        if self.last_data_point is not None:
            now_data_point = ParsedDataPoint.from_date_time(
                datetime.now(), self.last_data_point
            )

            while self.last_data_point != now_data_point:
                next_month = self.last_data_point.get_next_month()
                self.time_series.append(next_month.response_dict())
                self.last_data_point = next_month

    def json(self: any) -> List[dict]:
        return self.time_series
