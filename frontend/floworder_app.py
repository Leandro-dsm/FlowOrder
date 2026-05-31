import flet as ft
import requests
import re

# Cores 
COR_PRIMARIA = "#2563EB"
COR_SECUNDARIA = "#1D4ED8"
COR_SUCESSO = "#16A34A"
COR_FUNDO = "#F8FAFC"
COR_TEXTO = "#1E293B"

API_BASE = "http://localhost:5000/api"

def formatar_telefone(v):
    d = re.sub(r'\D', '', v)
    if len(d) >= 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:11]}"
    if len(d) >= 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:10]}"
    if len(d) >= 6:
        return f"({d[:2]}) {d[2:6]}-"
    if len(d) >= 3:
        return f"({d[:2]}) {d[2:]}"
    if len(d) >= 2:
        return f"({d[:2]})"
    return v

def snack(page, msg, cor=ft.colors.GREEN, icon=ft.icons.CHECK_CIRCLE):
    page.snack_bar = ft.SnackBar(
        content=ft.Row(
            controls=[
                ft.Icon(name=icon, size=20, color=ft.colors.WHITE),
                ft.Text(value=msg, size=14, weight=ft.FontWeight.W_500)
            ],
            spacing=10
        ),
        bgcolor=cor,
        duration=3000
    )
    page.snack_bar.open = True
    page.update()

def criar_campo(label, icone, width=280, helper=None, on_change=None):
    return ft.TextField(
        label=label,
        width=width,
        border_radius=8,
        prefix_icon=icone,
        bgcolor=ft.colors.WHITE,
        helper_text=helper,
        on_change=on_change
    )

def dialog_confirmar(page, titulo, conteudo, on_confirmar):
    dlg = ft.AlertDialog(
        title=ft.Text(value=titulo),
        content=ft.Text(value=conteudo),
        actions=[
            ft.TextButton(text="Cancelar", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
            ft.ElevatedButton(text="Excluir", on_click=on_confirmar, style=ft.ButtonStyle(bgcolor=ft.colors.RED_700, color=ft.colors.WHITE))
        ]
    )
    page.dialog = dlg
    dlg.open = True
    page.update()
    return dlg

def main(page: ft.Page):
    page.title = "FlowOrder"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = COR_FUNDO

    # ---------- Clientes ----------
    lista_clientes = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, height=400)
    nome = criar_campo("Nome completo", ft.icons.PERSON)
    email = criar_campo("E-mail", ft.icons.EMAIL)
    telefone = criar_campo(
        "Telefone", ft.icons.PHONE, helper="Digite apenas números - formata automática",
        on_change=lambda e: setattr(telefone, 'value', formatar_telefone(e.control.value)) if e.control.value else None
    )

    def carregar_clientes():
        try:
            r = requests.get(f"{API_BASE}/clientes")
            if r.status_code == 200:
                lista_clientes.controls.clear()
                dados = r.json()
                if not dados:
                    lista_clientes.controls.append(
                        ft.Container(
                            content=ft.Text(value="Nenhum cliente cadastrado.", italic=True, color=ft.colors.GREY_600),
                            alignment=ft.alignment.center,
                            padding=30
                        )
                    )
                else:
                    for c in dados:
                        lista_clientes.controls.append(
                            ft.Card(
                                elevation=2,
                                shape=ft.RoundedRectangleBorder(radius=10),
                                content=ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(name=ft.icons.PERSON_OUTLINE, color=ft.colors.BLUE_700, size=22),
                                                    ft.Text(value=c['nome'], weight=ft.FontWeight.BOLD, size=16),
                                                    ft.Row(
                                                        controls=[
                                                            ft.IconButton(icon=ft.icons.EDIT, icon_color=ft.colors.BLUE_600, tooltip="Editar",
                                                                          on_click=lambda e, cli=c: editar_cliente(cli)),
                                                            ft.IconButton(icon=ft.icons.DELETE, icon_color=ft.colors.RED_600, tooltip="Excluir",
                                                                          on_click=lambda e, cid=c['id']: deletar_cliente(cid))
                                                        ],
                                                        spacing=0
                                                    )
                                                ],
                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            ),
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(name=ft.icons.EMAIL_OUTLINED, size=16, color=ft.colors.GREY_600),
                                                    ft.Text(value=c['email'], size=13)
                                                ],
                                                spacing=8
                                            ),
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(name=ft.icons.PHONE_OUTLINED, size=16, color=ft.colors.GREY_600),
                                                    ft.Text(value=c['telefone'], size=13)
                                                ],
                                                spacing=8
                                            )
                                        ],
                                        spacing=8
                                    ),
                                    padding=15
                                )
                            )
                        )
                page.update()
        except:
            snack(page, "Erro ao carregar clientes", ft.colors.RED, ft.icons.ERROR)

    def deletar_cliente(cliente_id):
        def confirmar(e):
            try:
                r = requests.delete(f"{API_BASE}/clientes/{cliente_id}")
                if r.status_code == 200:
                    snack(page, "Cliente excluído!")
                    carregar_clientes()
                    carregar_clientes_dropdown()
                else:
                    snack(page, "Erro ao excluir", ft.colors.RED, ft.icons.ERROR)
            except:
                snack(page, "Falha na conexão", ft.colors.RED, ft.icons.CLOUD_OFF)
            page.dialog.open = False
            page.update()
        dialog_confirmar(page, "Confirmar exclusão", "Tem certeza que deseja excluir este cliente?", confirmar)

    def editar_cliente(cliente):
        nome_ed = criar_campo("Nome", ft.icons.PERSON, width=300)
        email_ed = criar_campo("E-mail", ft.icons.EMAIL, width=300)
        tel_ed = criar_campo("Telefone", ft.icons.PHONE, width=300,
                             on_change=lambda e: setattr(tel_ed, 'value', formatar_telefone(e.control.value)) if e.control.value else None)
        nome_ed.value = cliente['nome']
        email_ed.value = cliente['email']
        tel_ed.value = cliente['telefone']
        dlg = ft.AlertDialog(
            title=ft.Text(value="Editar Cliente"),
            content=ft.Column(controls=[nome_ed, email_ed, tel_ed], spacing=10),
            actions=[
                ft.TextButton(text="Cancelar", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                ft.ElevatedButton(text="Salvar", on_click=lambda e: salvar_edicao_cliente(cliente['id'], nome_ed.value, email_ed.value, tel_ed.value, dlg))
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def salvar_edicao_cliente(cid, nome_val, email_val, telefone_val, dlg):
        try:
            r = requests.put(f"{API_BASE}/clientes/{cid}", json={"nome": nome_val, "email": email_val, "telefone": telefone_val})
            if r.status_code == 200:
                snack(page, "Cliente atualizado!")
                carregar_clientes()
                carregar_clientes_dropdown()
            else:
                snack(page, "Erro na atualização", ft.colors.RED)
        except:
            snack(page, "Falha na conexão", ft.colors.RED)
        dlg.open = False
        page.update()

    def adicionar_cliente(e):
        if not nome.value:
            snack(page, "Nome obrigatório", ft.colors.RED, ft.icons.WARNING)
            return
        try:
            r = requests.post(f"{API_BASE}/clientes", json={"nome": nome.value, "email": email.value, "telefone": telefone.value})
            if r.status_code == 201:
                snack(page, "Cliente adicionado!")
                nome.value = ""
                email.value = ""
                telefone.value = ""
                carregar_clientes()
                carregar_clientes_dropdown()
            else:
                erro = r.json().get('erro', 'Erro')
                snack(page, erro, ft.colors.RED)
        except:
            snack(page, "Falha na conexão", ft.colors.RED, ft.icons.CLOUD_OFF)
        page.update()

    btn_cliente = ft.ElevatedButton(
        text="Salvar Cliente",
        icon=ft.icons.SAVE,
        on_click=adicionar_cliente,
        style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=COR_PRIMARIA, shape=ft.RoundedRectangleBorder(radius=8), padding=15)
    )

    campos_cliente = ft.ResponsiveRow(
        controls=[
            ft.Column(col={"sm": 12, "md": 4}, controls=[nome]),
            ft.Column(col={"sm": 12, "md": 4}, controls=[email]),
            ft.Column(col={"sm": 12, "md": 4}, controls=[telefone])
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER
    )

    view_clientes = ft.Column(
        controls=[
            ft.Text(value="➕ Novo Cliente", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            campos_cliente,
            ft.Row(controls=[btn_cliente], alignment=ft.MainAxisAlignment.END),
            ft.Divider(height=20),
            ft.Text(value="📋 Lista de Clientes", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_800),
            lista_clientes
        ],
        spacing=15
    )

    # ---------- Pedidos ----------
    lista_pedidos = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, height=400)
    cliente_drop = ft.Dropdown(width=280, label="Selecione o cliente", border_radius=8, prefix_icon=ft.icons.PEOPLE, bgcolor=ft.colors.WHITE)
    produto = criar_campo("Produto", ft.icons.SHOPPING_CART)
    valor = criar_campo("Valor (R$)", ft.icons.ATTACH_MONEY, helper="0,00")

    def carregar_pedidos():
        try:
            r = requests.get(f"{API_BASE}/pedidos")
            if r.status_code == 200:
                lista_pedidos.controls.clear()
                dados = r.json()
                if not dados:
                    lista_pedidos.controls.append(
                        ft.Container(
                            content=ft.Text(value="Nenhum pedido registrado.", italic=True, color=ft.colors.GREY_600),
                            alignment=ft.alignment.center,
                            padding=30
                        )
                    )
                else:
                    for p in dados:
                        lista_pedidos.controls.append(
                            ft.Card(
                                elevation=2,
                                shape=ft.RoundedRectangleBorder(radius=10),
                                content=ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(name=ft.icons.RECEIPT, color=ft.colors.GREEN_700, size=22),
                                                    ft.Text(value=f"Pedido #{p['id']}", weight=ft.FontWeight.BOLD, size=16),
                                                    ft.Row(
                                                        controls=[
                                                            ft.IconButton(icon=ft.icons.EDIT, icon_color=ft.colors.BLUE_600, tooltip="Editar",
                                                                          on_click=lambda e, ped=p: editar_pedido(ped)),
                                                            ft.IconButton(icon=ft.icons.DELETE, icon_color=ft.colors.RED_600, tooltip="Excluir",
                                                                          on_click=lambda e, pid=p['id']: deletar_pedido(pid))
                                                        ],
                                                        spacing=0
                                                    )
                                                ],
                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            ),
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(name=ft.icons.PERSON_OUTLINE, size=16, color=ft.colors.GREY_600),
                                                    ft.Text(value=f"Cliente: {p.get('nome_cliente', '?')}", size=13)
                                                ],
                                                spacing=8
                                            ),
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(name=ft.icons.SHOPPING_CART, size=16, color=ft.colors.GREY_600),
                                                    ft.Text(value=f"Produto: {p['produto']}", size=13)
                                                ],
                                                spacing=8
                                            ),
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(name=ft.icons.ATTACH_MONEY, size=16, color=ft.colors.GREY_600),
                                                    ft.Text(value=f"Valor: R$ {p['valor']:.2f}", size=13, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_800)
                                                ],
                                                spacing=8
                                            )
                                        ],
                                        spacing=8
                                    ),
                                    padding=15
                                )
                            )
                        )
                page.update()
        except:
            snack(page, "Erro ao carregar pedidos", ft.colors.RED, ft.icons.ERROR)

    def deletar_pedido(pedido_id):
        def confirmar(e):
            try:
                r = requests.delete(f"{API_BASE}/pedidos/{pedido_id}")
                if r.status_code == 200:
                    snack(page, "Pedido excluído!")
                    carregar_pedidos()
                else:
                    snack(page, "Erro ao excluir", ft.colors.RED)
            except:
                snack(page, "Falha na conexão", ft.colors.RED)
            page.dialog.open = False
            page.update()
        dialog_confirmar(page, "Confirmar exclusão", "Tem certeza que deseja excluir este pedido?", confirmar)

    def editar_pedido(pedido):
        cliente_ed = ft.Dropdown(label="Cliente", width=300)
        produto_ed = criar_campo("Produto", ft.icons.SHOPPING_CART, width=300)
        valor_ed = criar_campo("Valor (R$)", ft.icons.ATTACH_MONEY, width=300)
        produto_ed.value = pedido['produto']
        valor_ed.value = str(pedido['valor']).replace('.', ',')
        def carregar_clientes_edit():
            try:
                r = requests.get(f"{API_BASE}/clientes")
                if r.status_code == 200:
                    clientes_data = r.json()
                    cliente_ed.options = [ft.dropdown.Option(key=str(c['id']), text=c['nome']) for c in clientes_data]
                    for opt in cliente_ed.options:
                        if opt.key == str(pedido['id_cliente']):
                            cliente_ed.value = opt.key
                            break
                    page.update()
            except:
                pass
        carregar_clientes_edit()
        dlg = ft.AlertDialog(
            title=ft.Text(value="Editar Pedido"),
            content=ft.Column(controls=[cliente_ed, produto_ed, valor_ed], spacing=10),
            actions=[
                ft.TextButton(text="Cancelar", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                ft.ElevatedButton(text="Salvar", on_click=lambda e: salvar_edicao_pedido(pedido['id'], cliente_ed.value, produto_ed.value, valor_ed.value, dlg))
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def salvar_edicao_pedido(pid, cid, prod_str, val_str, dlg):
        try:
            val = float(val_str.replace(',', '.'))
        except:
            snack(page, "Valor inválido", ft.colors.RED)
            return
        try:
            r = requests.put(f"{API_BASE}/pedidos/{pid}", json={"id_cliente": int(cid), "produto": prod_str, "valor": val})
            if r.status_code == 200:
                snack(page, "Pedido atualizado!")
                carregar_pedidos()
            else:
                snack(page, "Erro na atualização", ft.colors.RED)
        except:
            snack(page, "Falha na conexão", ft.colors.RED)
        dlg.open = False
        page.update()

    def carregar_clientes_dropdown():
        try:
            r = requests.get(f"{API_BASE}/clientes")
            if r.status_code == 200:
                clientes_data = r.json()
                if clientes_data:
                    cliente_drop.options = [ft.dropdown.Option(key=str(c['id']), text=c['nome']) for c in clientes_data]
                else:
                    cliente_drop.options = [ft.dropdown.Option(key="", text="Nenhum cliente")]
                page.update()
        except:
            pass

    def adicionar_pedido(e):
        if not cliente_drop.value or not produto.value or not valor.value:
            snack(page, "Preencha todos os campos", ft.colors.RED, ft.icons.WARNING)
            return
        try:
            val = float(valor.value.replace(',', '.'))
        except:
            snack(page, "Valor inválido", ft.colors.RED, ft.icons.ERROR)
            return
        try:
            r = requests.post(f"{API_BASE}/pedidos", json={"id_cliente": int(cliente_drop.value), "produto": produto.value, "valor": val})
            if r.status_code == 201:
                snack(page, "Pedido registrado!")
                produto.value = ""
                valor.value = ""
                cliente_drop.value = None
                carregar_pedidos()
            else:
                erro = r.json().get('erro', 'Erro')
                snack(page, erro, ft.colors.RED)
        except:
            snack(page, "Falha na conexão", ft.colors.RED, ft.icons.CLOUD_OFF)
        page.update()

    btn_pedido = ft.ElevatedButton(
        text="Registrar Pedido",
        icon=ft.icons.SHOPPING_CART_CHECKOUT,
        on_click=adicionar_pedido,
        style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=COR_SUCESSO, shape=ft.RoundedRectangleBorder(radius=8), padding=15)
    )

    campos_pedido = ft.ResponsiveRow(
        controls=[
            ft.Column(col={"sm": 12, "md": 4}, controls=[cliente_drop]),
            ft.Column(col={"sm": 12, "md": 4}, controls=[produto]),
            ft.Column(col={"sm": 12, "md": 4}, controls=[valor])
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER
    )

    view_pedidos = ft.Column(
        controls=[
            ft.Text(value="➕ Novo Pedido", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_900),
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            campos_pedido,
            ft.Row(controls=[btn_pedido], alignment=ft.MainAxisAlignment.END),
            ft.Divider(height=20),
            ft.Text(value="📦 Lista de Pedidos", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_800),
            lista_pedidos
        ],
        spacing=15
    )

    # Abas
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Clientes", icon=ft.icons.PEOPLE, content=ft.Container(content=view_clientes, padding=10)),
            ft.Tab(text="Pedidos", icon=ft.icons.SHOPPING_BAG, content=ft.Container(content=view_pedidos, padding=10))
        ],
        expand=True,
        indicator_color=COR_PRIMARIA
    )

    # Cabeçalho
    # ========== CABEÇALHO (igual à landing page) ==========
    cabecalho = ft.Container(
    content=ft.Column(
        controls=[
            ft.Text(value="FlowOrder", size=48, weight=ft.FontWeight.BOLD, color=COR_PRIMARIA),
            ft.Text(value="Sistema de Gestão de Clientes e Pedidos", size=20, color=COR_TEXTO),
            ft.Text(
                value="Aplicação Full Stack desenvolvida com Flask, Flet e Swagger para gerenciamento de clientes e pedidos através de uma interface moderna e integrada a uma API REST.",
                size=14,
                color=ft.colors.GREY_600,
                text_align=ft.TextAlign.CENTER,
                width=700
            ),
            ft.Row(
                controls=[
                    ft.OutlinedButton(
                        text="Repositório GitHub",
                        icon=ft.icons.CODE,
                        on_click=lambda e: page.launch_url("https://github.com/Leandro-dsm/FlowOrder"),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    ),
                    ft.ElevatedButton(
                        text="Swagger API",
                        icon=ft.icons.API,
                        on_click=lambda e: page.launch_url("http://localhost:5000/apidocs"),
                        style=ft.ButtonStyle(bgcolor=COR_PRIMARIA, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8))
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15
    ),
    padding=ft.padding.symmetric(vertical=30, horizontal=20),
    bgcolor=ft.colors.WHITE,
    border_radius=20,
    margin=ft.margin.only(bottom=25),
    shadow=[ft.BoxShadow(blur_radius=10, spread_radius=1, color=ft.colors.BLACK12)]
)

    page.add(cabecalho, tabs)
    carregar_clientes()
    carregar_pedidos()
    carregar_clientes_dropdown()

ft.app(target=main, view=ft.AppView.WEB_BROWSER)