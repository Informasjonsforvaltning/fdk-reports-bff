from flask_restful import Resource


class Ping(Resource):
    def get(self):
        return 200


class Ready(Resource):
    def get(self):
        return 200


class InformationModelsReport(Resource):
    def get(self):
        return 501


class DataServicesReport(Resource):
    def get(self):
        return 501


class DataSetsReport(Resource):
    def get(self):
        return 501


class ConceptsReport(Resource):
    def get(self):
        return 501
