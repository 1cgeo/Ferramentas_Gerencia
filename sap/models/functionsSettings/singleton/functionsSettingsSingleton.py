from Ferramentas_Gerencia.sap.models.functionsSettings.functionsSettings  import FunctionsSettings

class FunctionsSettingsSingleton:

    functionsSettings = None

    @staticmethod
    def getInstance():
        if not FunctionsSettingsSingleton.functionsSettings:
            FunctionsSettingsSingleton.functionsSettings = FunctionsSettings()
        return FunctionsSettingsSingleton.functionsSettings