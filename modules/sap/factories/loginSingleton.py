from Ferramentas_Gerencia.modules.sap.dialogs.login  import Login

class LoginSingleton:

    login = None

    @staticmethod
    def getInstance(loginCtrl):
        if not LoginSingleton.login:
            LoginSingleton.login = Login(loginCtrl)
        return LoginSingleton.login