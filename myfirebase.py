from kivy.app import App
import requests

class MyFireBase():
    API_KEY =  'AIzaSyCqOOBk1koLTBSMB-EiuBxsuQUvOByOLXQ'

    def criar_conta(self, email, senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}'
        info={'email':email,'password':senha,'returnSecureToken':True}
        requesicao = requests.post(link,data=info)
        requesicao_dic = requesicao.json() 

        if requesicao.ok:
            print('Usuario criado')
            idToken = requesicao_dic['idToken']
            refresh_token = requesicao_dic['refreshToken']
            local_id =  requesicao_dic['localId'] 
            my_app = App.get_running_app()
            my_app.local_id = local_id 
            my_app.id_token = idToken

            with open('refreshtoken.txt','w') as arquivo:
                arquivo.write(refresh_token)

            req_id = requests.get(f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={idToken}')
            id_vendedor = req_id.json()

            link = f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/{local_id}.json?auth={idToken}'
            info_usuario = f'{{"avatar":"foto1.png","equipe":"","total_vendas":"0","vendas":"","id_vendedor":"{id_vendedor}"}}'
            requesicao_usuario = requests.patch(link,data=info_usuario)

            proximo_id_vendedor = int(id_vendedor) + 1
            info_id_vendedor = f'{{"proximo_id_vendedor":"{proximo_id_vendedor}"}}'
            atualizar_proximo_id_vendedor = requests.patch(f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/.json?auth={idToken}',data=info_id_vendedor)

            my_app.carregar_infos_usuario()
            my_app.mudar_tela('homepage')

        else:
            mensagem_erro = requesicao_dic['error']['message']
            pagina_login = App.get_running_app().root.ids['loginpage']
            match mensagem_erro:
                case 'INVALID_EMAIL':
                    pagina_login.ids['mensagem_login'].text = 'Email inválido'
                    pagina_login.ids['mensagem_login'].color = (1,0,0,1)

                case 'MISSING_PASSWORD':
                    pagina_login.ids['mensagem_login'].text = 'Senha faltando'
                    pagina_login.ids['mensagem_login'].color = (1,0,0,1)

                case 'WEAK_PASSWORD : Password should be at least 6 characters':
                    pagina_login.ids['mensagem_login'].text = 'Senha fraca | digite ao menos 6 caracteres'
                    pagina_login.ids['mensagem_login'].color = (1,0,0,1)

                case 'EMAIL_EXISTS':
                    pagina_login.ids['mensagem_login'].text = 'Esse e-mail já existe!'
                    pagina_login.ids['mensagem_login'].color = (1,0,0,1)

                case _:
                    pagina_login.ids['mensagem_login'].text = f'{mensagem_erro}'
                    pagina_login.ids['mensagem_login'].color = (1,0,0,1)

    def fazer_login(self, email, senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}'
        info={'email':email,'password':senha,'returnSecureToken':True}
        requesicao = requests.post(link,data=info)
        requesicao_dic = requesicao.json() 

        if requesicao.ok:
            idToken = requesicao_dic['idToken']
            refresh_token = requesicao_dic['refreshToken']
            local_id =  requesicao_dic['localId'] 
            my_app = App.get_running_app()
            my_app.local_id = local_id 
            my_app.id_token = idToken

            with open('refreshtoken.txt','w') as arquivo:
                arquivo.write(refresh_token)

            my_app.carregar_infos_usuario()
            my_app.mudar_tela('homepage')

        else:
            mensagem_erro = requesicao_dic['error']['message']
            pagina_login = App.get_running_app().root.ids['loginpage']
            match mensagem_erro:
                case 'INVALID_EMAIL':
                    pagina_login.ids['mensagem_login'].text = 'Email inválido'
                    pagina_login.ids['mensagem_login'].color = (1,0,0,1)

                case 'MISSING_PASSWORD':
                    pagina_login.ids['mensagem_login'].text = 'Senha faltando'
                    pagina_login.ids['mensagem_login'].color = (1,0,0,1)

                case 'WEAK_PASSWORD : Password should be at least 6 characters':
                    pagina_login.ids['mensagem_login'].text = 'Senha fraca | digite ao menos 6 caracteres'
                    pagina_login.ids['mensagem_login'].color = (1,0,0,1)

                case 'EMAIL_EXISTS':
                    pagina_login.ids['mensagem_login'].text = 'Esse e-mail já existe!'
                    pagina_login.ids['mensagem_login'].color = (1,0,0,1)

                case 'INVALID_LOGIN_CREDENTIALS':
                    pagina_login.ids['mensagem_login'].text = 'Esse email não existe'
                    pagina_login.ids['mensagem_login'].color = (1,0,0,1)

                case _:
                    pagina_login.ids['mensagem_login'].text = f'{mensagem_erro}'
                    pagina_login.ids['mensagem_login'].color = (1,0,0,1)

    def trocar_token(self,):
        with open('refreshtoken.txt','r') as arquivo:
            refresh_token = arquivo.read()

        link = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'
        info = {'grant_type':'refresh_token','refresh_token':refresh_token}
        requesicao = requests.post(link,data=info)
        requesicao_dic = requesicao.json()
        local_id = requesicao_dic['user_id']
        id_token = requesicao_dic['id_token']

        return local_id,id_token
