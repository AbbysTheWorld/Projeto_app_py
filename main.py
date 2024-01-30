from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
from functools import partial
from bannervenda import BannerVenda
from bannervendedor import BannerVendedor
from pathlib import Path
from myfirebase import MyFireBase
from datetime import datetime
import certifi
import os

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
        for foto in Path('icones/fotos_perfil').iterdir():
            perfil = ImageButton(source=f'{foto}',on_release=partial(self.mudar_foto_perfil,foto))
            lista_fotoperfils = self.root.ids['fotoperfilpage'].ids['lista_fotosperfils'].add_widget(perfil)
        
    def carregar_infos_usuario(self):
        try:
            with open('refreshtoken.txt','r') as arquivo:
                refreshtoken = arquivo.read()

            local_id,id_token = self.firebase.trocar_token()

            self.local_id = local_id
            self.id_token = id_token

            requesicao = requests.get(f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}')
            requesicao_dic = requesicao.json()

            avatar = requesicao_dic['avatar']
            self.avatar = avatar
            self.root.ids['foto_perfil'].source = 'icones/fotos_perfil/{}'.format(avatar)

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
                    banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"],produto = venda["produto"], 
                                        foto_produto=venda["foto_produto"],data=venda['data'], preco=venda['preco'],
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
    
    def mudar_tela(self,id_tela):

        gerenciar_telas = self.root.ids['screen_manager']
        gerenciar_telas.current = id_tela

    def mudar_foto_perfil(self,foto,*args):
        self.root.ids['foto_perfil'].source = f'{foto}'

        info = f'{{"avatar":"{foto.name}"}}'

        requesicao = requests.patch(f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',
                                    data=str(info))
        
        self.mudar_tela('ajustespage')

    def adicionar_vendedor(self,id_vendedor_adicionado):
        try:
            link = f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'
            requesicao = requests.get(link)
            requesicao_dic = requesicao.json()

            pagina_adicionarvendedor = self.root.ids['adicionarvendedorpage']
            mensagem_texto = pagina_adicionarvendedor.ids['mensagem_outrovendedor']
            
            if requesicao_dic == {}:
                mensagem_texto.text = 'Usuário não encontrado'
            else:
                equipe = self.equipe.split(',')
                if id_vendedor_adicionado in equipe:
                    mensagem_texto.text = 'Vendedor já faz parte da equipe'
                else:
                    self.equipe = self.equipe + f",{id_vendedor_adicionado}"
                    info_equipe = f'{{"equipe":"{self.equipe}"}}'
                    requests.patch(f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',data=info_equipe)
                    pagina_listavendedores = self.root.ids['listarvendedorespage']
                    lista_vendedores = pagina_listavendedores.ids['lista_vendedores']
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adicionado)
                    lista_vendedores.add_widget(banner_vendedor)
                
                    mensagem_texto.text = 'Vendedor adicionado com sucesso'
        except:
            mensagem_texto.text = 'Usuário não encontrado'

    def carregar_scroll_views_venda(self):
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        label_data = pagina_adicionarvendas.ids['label_data']
        label_data.text = f'Data: {datetime.today().strftime("%d/%m/%Y")}'

        arquivo = Path('icones/fotos_clientes')
        arquivo2 = Path('icones/fotos_produtos')
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        lista_clientes = pagina_adicionarvendas.ids['lista_clientes']
        lista_clientes2 = pagina_adicionarvendas.ids['lista_clientes2']
        for foto_cliente in arquivo.iterdir():
            imagem =  ImageButton(source=f'icones/fotos_clientes/{foto_cliente.name}',on_release=partial(self.selecionar_cliente,foto_cliente.name))
            nome_cliente = foto_cliente.name.replace('.png','').capitalize()
            label = LabelButton(text=f'{nome_cliente}',on_release=partial(self.selecionar_cliente,foto_cliente.name))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)

        for foto_produto in arquivo2.iterdir():
            imagem =  ImageButton(source=f'icones/fotos_produtos/{foto_produto.name}',on_release=partial(self.selecionar_produto,foto_produto.name))
            nome_produto = foto_produto.name.replace('.png','').capitalize()
            label = LabelButton(text=f'{nome_produto}',on_release=partial(self.selecionar_produto,foto_produto.name))
            lista_clientes2.add_widget(imagem)
            lista_clientes2.add_widget(label)

    def selecionar_cliente(self,foto,*args):
        self.cliente = foto.replace('.png','')
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        lista_clientes = pagina_adicionarvendas.ids['lista_clientes']

        for item in list(lista_clientes.children):
            item.color = (1,1,1,1)
            try:
                texto = item.text
                texto = texto.lower()
                texto = texto + '.png'
                if foto == texto:
                    item.color = (0,207/255,219/255,1)
            except:
                pass

    def selecionar_produto(self,foto,*args):
        self.produto = foto.replace('.png','')
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        lista_clientes2 = pagina_adicionarvendas.ids['lista_clientes2']

        for item in list(lista_clientes2.children):
            item.color = (1,1,1,1)
            try:
                texto = item.text
                texto = texto.lower()
                texto = texto + '.png'
                if foto == texto:
                    item.color = (0,207/255,219/255,1)
            except:
                pass

    def selecionar_unidade(self,id_label,*args):
        self.unidade = id_label.replace('unidades_','')
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        pagina_adicionarvendas.ids['unidades_kg'].color = (1,1,1,1)
        pagina_adicionarvendas.ids['unidades_unidades'].color = (1,1,1,1)
        pagina_adicionarvendas.ids['unidades_litros'].color = (1,1,1,1)

        pagina_adicionarvendas.ids[id_label].color = (0,207/255,219/255,1)

    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade      

        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        data = pagina_adicionarvendas.ids['label_data'].text.replace('Data: ','')
        preco = pagina_adicionarvendas.ids['preco_total'].text
        quantidade = pagina_adicionarvendas.ids['quantidade'].text

        if not cliente:
            pagina_adicionarvendas.ids['label_selecione_cliente'].color = (1,0,0,1)
        else:
            pagina_adicionarvendas.ids['label_selecione_cliente'].color = (1,1,1,1)  
        if not produto:
            pagina_adicionarvendas.ids['label_selecione_produto'].color = (1,0,0,1)
        else:
            pagina_adicionarvendas.ids['label_selecione_produto'].color = (1,1,1,1)
        if not unidade:
            pagina_adicionarvendas.ids['unidades_kg'].color = (1,0,0,1)
            pagina_adicionarvendas.ids['unidades_unidades'].color = (1,0,0,1)
            pagina_adicionarvendas.ids['unidades_litros'].color = (1,0,0,1)
        if not preco:
            pagina_adicionarvendas.ids['label_preco'].color = (1,0,0,1)
        else:
            try:
                preco = float(preco)
                pagina_adicionarvendas.ids['label_preco'].color = (1,1,1,1)
            except:
                pagina_adicionarvendas.ids['label_preco'].color = (1,0,0,1)
        if not quantidade:
            pagina_adicionarvendas.ids['label_quantidade'].color = (1,0,0,1)
        else:
            try:
                pagina_adicionarvendas.ids['label_quantidade'].color = (1,1,1,1)
                quantidade = float(quantidade)
            except:
                pagina_adicionarvendas.ids['label_quantidade'].color = (1,0,0,1)

        if cliente and produto and unidade and preco and quantidade and (type(preco)==float) and (type(quantidade)==float):
            foto_produto = produto + '.png'
            foto_cliente = cliente + '.png'

            info = f'{{"cliente":"{cliente}","produto":"{produto}","foto_cliente":"{foto_cliente}","foto_produto":"{foto_produto}","data":"{data}","unidade":"{unidade}","preco":"{preco}","quantidade":"{quantidade}"}}'
            
            requests.post(f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}',data=info)

            banner = BannerVenda(cliente=cliente,produto=produto,foto_cliente=foto_cliente,foto_produto=foto_produto,
                                 data=data,preco=preco,quantidade=quantidade,unidade=unidade)
            
            homepage = self.root.ids['homepage']
            lista_vendas = homepage.ids['lista_venda']
            lista_vendas.add_widget(banner)

            requesicao = requests.get(f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}')
            total_vendas = float(requesicao.json())
            total_vendas += preco
            info = f'{{"total_vendas":"{total_vendas}"}}'
            requests.patch(f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',data=info)
            homepage.ids['label_total_vendas'].text = f'[color=000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'

            self.mudar_tela('homepage')

        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_vendas(self):
        pagina_todasvendas = self.root.ids['todasvendaspage']
        lista_vendas = pagina_todasvendas.ids['lista_venda']

        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        self.mudar_tela('todasvendaspage')
        requesicao = requests.get(f'https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requesicao_dic = requesicao.json()

        self.root.ids['foto_perfil'].source = 'icones/fotos_perfil/hash.png'

        total_vendas = 0
        for local_id_usuario in requesicao_dic:
            try:
                vendas = requesicao_dic[local_id_usuario]['vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda['preco'])
                    banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"],produto = venda["produto"], 
                                        foto_produto=venda["foto_produto"],data=venda['data'], preco=venda['preco'],
                                        unidade=venda['unidade'], quantidade=venda["quantidade"])
                    lista_vendas.add_widget(banner)
            except:
                pass

        pagina_todasvendas.ids['label_total_vendas'].text = f'[color=000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'

    def sair_todas_vendas(self):
        self.root.ids['foto_perfil'].source = f'icones/fotos_perfil/{self.avatar}'
        self.mudar_tela('ajustespage')
    
    def sair_outras_vendasvendedor(self):
        self.root.ids['foto_perfil'].source = f'icones/fotos_perfil/{self.avatar}'
        self.mudar_tela('homepage')

    def carregar_vendas_vendedor(self,dic_info_vendedor,*args):
        self.mudar_tela('vendasoutrovendedorpage')
        
        total_vendas = dic_info_vendedor['total_vendas']
        pagina_vendasoutrovendedor = self.root.ids['vendasoutrovendedorpage']
        lista_vendas = pagina_vendasoutrovendedor.ids['lista_vendas']

        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)
        try:
            vendas = dic_info_vendedor['vendas']
            pagina_vendasoutrovendedor.ids['label_total_vendas'].text = f'[color=000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'
            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"],produto = venda["produto"], 
                                    foto_produto=venda["foto_produto"],data=venda['data'], preco=venda['preco'],
                                    unidade=venda['unidade'], quantidade=venda["quantidade"])
                lista_vendas.add_widget(banner)
        except Exception as ex:
            pass
        avatar = dic_info_vendedor['avatar']
        self.root.ids['foto_perfil'].source = f'icones/fotos_perfil/{avatar}'

MainApp().run()

#https://aplicativovendashash-8570e-default-rtdb.firebaseio.com/
#get
#post
#patch