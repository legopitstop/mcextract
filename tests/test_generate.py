from mcextract import MCExtractAPI

api = MCExtractAPI()
api.generate("1.20.6", ['--client', '--server', '--reports'], accept_eula=True)
