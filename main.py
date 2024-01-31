from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
import requests
from functools import partial
from bannervenda import BannerVenda
from bannervendedor import BannerVendedor
from myfirebase import MyFireBase
from datetime import datetime
import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

GUI = Builder.load_file('main.kv')

class MainApp(App):
    cliente = None
    unidade = None
    produto = None

    def build(self):
        self.firebase = MyFireBase()
        return GUI

    def on_start(self):
        self.carregar_infos_usuario()
        self.carregar_perfils_usuario()
        self.carregar_scroll_views_venda()

    def carregar_perfils_usuario(self):
        for foto in os.listdir('icones/fotos_perfil'):
            perfil = ImageButton(source=f'{os.path.join("icones/fotos_perfil", foto)}',
                                 on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotoperfils = self.root.ids['fotoperfilpage'].ids['lista_fotosperfils'].add_widget(perfil)

    def carregar_infos_usuario(self):
        try:
            with open('refreshtoken.txt', 'r') as arquivo:
                refreshtoken = arquivo.read()

            local_id, id_token = self.firebase.trocar_token()

            self.local_id = local_id
            self.id_token = id_token

            requesicao = requests.get(f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}')
            requesicao_dic = requesicao.json()

            avatar = requesicao_dic['avatar']
            self.avatar = avatar
            self.root.ids['foto_perfil'].source = os.path.join('icones/fotos_perfil', avatar)

            id_vendedor = requesicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids['ajustespage']
            pagina_ajustes.ids['id_vendedor'].text = f'Seu ID Único: {id_vendedor}'

            total_vendas = requesicao_dic['total_vendas']
            self.total_vendas = total_vendas
            homepage = self.root.ids['homepage']
            lista_vendas = homepage.ids['lista_venda']

            homepage.ids['label_total_vendas'].text = f'[color=000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'
            self.equipe = requesicao_dic['equipe']

            try:
                vendas = requesicao_dic['vendas']
                self.vendas = vendas
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"],produto=venda["produto"],
                                         foto_produto=venda["foto_produto"], data=venda['data'], preco=venda['preco'],
                                         unidade=venda['unidade'], quantidade=venda["quantidade"])
                    lista_vendas.add_widget(banner)
            except Exception as ex:
                pass

            equipe = requesicao_dic['equipe']
            lista_equipe = equipe.split(',')
            pagina_listavendedores = self.root.ids['listarvendedorespage']
            lista_vendedores = pagina_listavendedores.ids['lista_vendedores']
            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != '':
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)

            self.mudar_tela('homepage')
        except:
            pass

    def mudar_tela(self, id_tela):
        gerenciar_telas = self.root.ids['screen_manager']
        gerenciar_telas.current = id_tela

    def mudar_foto_perfil(self, foto, *args):
        self.root.ids['foto_perfil'].source = os.path.join('icones/fotos_perfil', foto)

        info = f'{{"avatar":"{foto}"}}'

        requesicao = requests.patch(f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',
                                    data=str(info))

        self.mudar_tela('ajustespage')

    # Restante do código mantido...
    # ...
    # ...

if __name__ == "__main__":
    MainApp().run()
