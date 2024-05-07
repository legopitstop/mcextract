from mcextract import MCExtractAPI

api = MCExtractAPI()
api.extract("1.20.4/1.20.4.jar", True, True, accept_eula=False)
