import tkinter as tk
from tkinter import messagebox, ttk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
import sqlite3
import datetime

# Model - Responsável pela interação com o banco de dados
class AtendimentoModel:
    def __init__(self):
        self.conexao = sqlite3.connect('atendimentos.db')
        self.cursor = self.conexao.cursor()
        self._criar_tabelas()

    def _criar_tabelas(self):
        # Criar tabela de munícipes
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS municipes (
            cpf TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            endereco TEXT,
            telefone TEXT NOT NULL,
            rg TEXT
        )
        ''')

        # Criar tabela de atendimentos
        self.cursor.execute("PRAGMA table_info(atendimentos)")
        colunas = [info[1] for info in self.cursor.fetchall()]

        if 'cpf' not in colunas:
            # Recriar a tabela de atendimentos com a coluna cpf
            self.cursor.execute('''
            DROP TABLE IF EXISTS atendimentos
            ''')
            self.cursor.execute('''
            CREATE TABLE atendimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT NOT NULL,
                tipo_pedido TEXT NOT NULL,
                descricao TEXT,
                anexos TEXT,
                data_horario TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pendente',
                FOREIGN KEY (cpf) REFERENCES municipes (cpf)
            )
            ''')
        self.conexao.commit()

    def registrar_municipe(self, cpf, nome, endereco, telefone, rg):
        self.cursor.execute('''
        INSERT OR IGNORE INTO municipes (cpf, nome, endereco, telefone, rg)
        VALUES (?, ?, ?, ?, ?)
        ''', (cpf, nome, endereco, telefone, rg))
        self.conexao.commit()

    def buscar_municipe(self, cpf):
        self.cursor.execute('''
        SELECT * FROM municipes WHERE cpf = ?
        ''', (cpf,))
        return self.cursor.fetchone()

    def atualizar_municipe(self, cpf, nome, endereco, telefone, rg):
        self.cursor.execute('''
        UPDATE municipes
        SET nome = ?, endereco = ?, telefone = ?, rg = ?
        WHERE cpf = ?
        ''', (nome, endereco, telefone, rg, cpf))
        self.conexao.commit()

    def registrar_atendimento(self, cpf, tipo_pedido, descricao, anexos, data_horario, status):
        self.cursor.execute('''
        INSERT INTO atendimentos (cpf, tipo_pedido, descricao, anexos, data_horario, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (cpf, tipo_pedido, descricao, anexos, data_horario, status))
        self.conexao.commit()

    def consultar_atendimentos(self, filtro_nome=None, filtro_cpf=None):
        query = '''
        SELECT a.*, m.nome, m.telefone FROM atendimentos a
        JOIN municipes m ON a.cpf = m.cpf
        '''
        parametros = []

        if filtro_nome or filtro_cpf:
            query += " WHERE"
            condicoes = []
            if filtro_nome:
                condicoes.append(" m.nome LIKE ?")
                parametros.append(f"%{filtro_nome}%")
            if filtro_cpf:
                condicoes.append(" m.cpf = ?")
                parametros.append(filtro_cpf)
            query += " AND ".join(condicoes)

        self.cursor.execute(query, parametros)
        return self.cursor.fetchall()

    def atualizar_atendimento(self, atendimento_id, cpf, tipo_pedido, descricao, status):
        self.cursor.execute('''
        UPDATE atendimentos
        SET cpf = ?, tipo_pedido = ?, descricao = ?, status = ?
        WHERE id = ?
        ''', (cpf, tipo_pedido, descricao, status, atendimento_id))
        self.conexao.commit()

    def consultar_municipes(self):
        self.cursor.execute('''
        SELECT * FROM municipes
        ''')
        return self.cursor.fetchall()

    def fechar_conexao(self):
        self.conexao.close()

# Controller - Responsável pela lógica da aplicação
class AtendimentoController:
    def __init__(self, model):
        self.model = model

    def registrar_municipe(self, cpf, nome, endereco, telefone, rg):
        self.model.registrar_municipe(cpf, nome, endereco, telefone, rg)

    def buscar_municipe(self, cpf):
        return self.model.buscar_municipe(cpf)
    
    def atualizar_municipe(self, cpf, nome, endereco, telefone, rg):
        self.model.atualizar_municipe(cpf, nome, endereco, telefone, rg)

    def registrar_atendimento(self, cpf, tipo_pedido, descricao, anexos, status="Pendente"):
        data_horario = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.model.registrar_atendimento(cpf, tipo_pedido, descricao, anexos, data_horario, status)

    def consultar_atendimentos(self, filtro_nome=None, filtro_cpf=None):
        return self.model.consultar_atendimentos(filtro_nome, filtro_cpf)
    
    def atualizar_atendimento(self, atendimento_id, cpf, tipo_pedido, descricao, status):
        self.model.atualizar_atendimento(atendimento_id, cpf, tipo_pedido, descricao, status)

    def consultar_municipes(self):
        return self.model.consultar_municipes()

    def gerar_relatorio_pdf(self, atendimentos, caminho_pdf="relatorio_atendimentos.pdf"):
        c = pdf_canvas.Canvas(caminho_pdf, pagesize=letter)
        c.setFont("Helvetica", 10)
        c.drawString(100, 750, "Relatório Completo de Atendimentos")
        c.drawString(100, 735, "-" * 80)

        y = 720
        for atendimento in atendimentos:
            c.drawString(100, y, f"ID: {atendimento[0]}")
            c.drawString(100, y - 15, f"CPF: {atendimento[1]}")
            c.drawString(100, y - 30, f"Nome: {atendimento[7]}")
            c.drawString(100, y - 45, f"Telefone: {atendimento[8]}")
            c.drawString(100, y - 60, f"Tipo de Pedido: {atendimento[2]}")
            c.drawString(100, y - 75, f"Descrição: {atendimento[3]}")
            c.drawString(100, y - 90, f"Anexos: {atendimento[4]}")
            c.drawString(100, y - 105, f"Data/Horário: {atendimento[5]}")
            c.drawString(100, y - 120, f"Status: {atendimento[6]}")
            y -= 150

            if y < 50:
                c.showPage()  # Cria uma nova página se o espaço acabar
                c.setFont("Helvetica", 10)
                y = 750

        c.save()
        print(f"Relatório salvo em {caminho_pdf}")

# Telas do sistema
# Tela de Registro de Atendimento
class RegistroAtendimentoView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        # Campos de Registro
        ttk.Label(self, text="CPF:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entrada_cpf = ttk.Entry(self, width=50)
        self.entrada_cpf.grid(row=0, column=1, pady=2)

        ttk.Label(self, text="Tipo de Pedido:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.tipo_pedido_var = tk.StringVar()
        self.tipo_pedido_var.set("Selecione o tipo de pedido")
        self.tipo_pedido_dropdown = ttk.Combobox(self, textvariable=self.tipo_pedido_var, values=[
            "Reclamação de Serviço Público", "Solicitação de Apoio para Saúde", "Pedido de Melhorias no Bairro",
            "Solicitação de Evento Comunitário", "Agradecimento ao Vereador", "Proposta de Projeto para a Comunidade",
            "Solicitação de Atendimento Animal", "Denúncia de Maus-Tratos a Animais"
        ], state="readonly", width=47)
        self.tipo_pedido_dropdown.grid(row=1, column=1, pady=2)

        ttk.Label(self, text="Descrição:").grid(row=2, column=0, sticky=tk.NW, pady=2)
        self.entrada_descricao = tk.Text(self, width=50, height=5)
        self.entrada_descricao.grid(row=2, column=1, pady=2)

        ttk.Button(self, text="Salvar Atendimento", command=self.salvar_atendimento).grid(row=3, column=1, sticky=tk.W, pady=10)
        ttk.Button(self, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).grid(row=4, column=1, sticky=tk.W, pady=10)

    def salvar_atendimento(self):
        cpf = self.entrada_cpf.get()
        tipo_pedido = self.tipo_pedido_var.get()
        descricao = self.entrada_descricao.get("1.0", tk.END)
        anexos = ""

        if cpf and tipo_pedido != "Selecione o tipo de pedido":
            self.controller.registrar_atendimento(cpf, tipo_pedido, descricao, anexos)
            messagebox.showinfo("Sucesso", "Atendimento registrado com sucesso!")
            self.switch_view(DashboardView)
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")

# Tela de Registro de Munícipe
class RegistroMunicipeView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        # Campos de Registro
        ttk.Label(self, text="CPF:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entrada_cpf = ttk.Entry(self, width=50)
        self.entrada_cpf.grid(row=0, column=1, pady=2)

        ttk.Label(self, text="Nome:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entrada_nome = ttk.Entry(self, width=50)
        self.entrada_nome.grid(row=1, column=1, pady=2)

        ttk.Label(self, text="Endereço:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entrada_endereco = ttk.Entry(self, width=50)
        self.entrada_endereco.grid(row=2, column=1, pady=2)

        ttk.Label(self, text="Telefone:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entrada_telefone = ttk.Entry(self, width=50)
        self.entrada_telefone.grid(row=3, column=1, pady=2)

        ttk.Label(self, text="RG:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.entrada_rg = ttk.Entry(self, width=50)
        self.entrada_rg.grid(row=4, column=1, pady=2)

        ttk.Button(self, text="Salvar Munícipe", command=self.salvar_municipe).grid(row=5, column=1, sticky=tk.W, pady=10)
        ttk.Button(self, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).grid(row=6, column=1, sticky=tk.W, pady=10)

    def salvar_municipe(self):
        cpf = self.entrada_cpf.get()
        nome = self.entrada_nome.get()
        endereco = self.entrada_endereco.get()
        telefone = self.entrada_telefone.get()
        rg = self.entrada_rg.get()

        if cpf and nome and telefone:
            self.controller.registrar_municipe(cpf, nome, endereco, telefone, rg)
            messagebox.showinfo("Sucesso", "Munícipe registrado com sucesso!")
            self.switch_view(DashboardView)
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")

# Tela de Histórico de Atendimentos
class HistoricoAtendimentoView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        # Campos de Filtro
        ttk.Label(self, text="Filtrar por Nome:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.filtro_nome = ttk.Entry(self, width=50)
        self.filtro_nome.grid(row=0, column=1, pady=2)

        ttk.Label(self, text="Filtrar por CPF:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.filtro_cpf = ttk.Entry(self, width=50)
        self.filtro_cpf.grid(row=1, column=1, pady=2)

        ttk.Button(self, text="Filtrar", command=self.carregar_atendimentos).grid(row=2, column=1, sticky=tk.W, pady=10)

        # Tabela Interativa
        self.treeview = ttk.Treeview(self, columns=("ID", "Nome", "Tipo de Pedido", "Status"), show="headings")
        self.treeview.heading("ID", text="ID")
        self.treeview.heading("Nome", text="Nome")
        self.treeview.heading("Tipo de Pedido", text="Tipo de Pedido")
        self.treeview.heading("Status", text="Status")
        self.treeview.grid(row=3, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

        # Botão para editar atendimento
        ttk.Button(self, text="Editar Atendimento Selecionado", command=self.editar_atendimento).grid(row=4, column=0, pady=10)

        # Botão para voltar ao Dashboard
        ttk.Button(self, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).grid(row=4, column=1, pady=10)

    def carregar_atendimentos(self):
        filtro_nome = self.filtro_nome.get()
        filtro_cpf = self.filtro_cpf.get()
        atendimentos = self.controller.consultar_atendimentos(filtro_nome, filtro_cpf)
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        for atendimento in atendimentos:
            self.treeview.insert("", "end", values=(atendimento[0], atendimento[7], atendimento[2], atendimento[6]))

    def editar_atendimento(self):
        try:
            selected_item = self.treeview.selection()[0]
            atendimento_data = self.treeview.item(selected_item)['values']
            atendimento_id = atendimento_data[0]
            EditarAtendimentoView(self, self.controller, atendimento_id)
        except IndexError:
            messagebox.showerror("Erro", "Por favor, selecione um atendimento para editar.")

# Tela de Edição de Atendimento
class EditarAtendimentoView(tk.Toplevel):
    def __init__(self, parent, controller, atendimento_id):
        super().__init__(parent)
        self.controller = controller
        self.atendimento_id = atendimento_id
        self.title("Editar Atendimento")
        self.geometry("600x500")
        self._construir_interface()

    def _construir_interface(self):
        # Recuperando os dados do atendimento a ser editado
        atendimento = self.controller.consultar_atendimentos()
        atendimento_dados = [a for a in atendimento if a[0] == self.atendimento_id][0]

        # Campo CPF
        ttk.Label(self, text="CPF:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cpf_var = tk.StringVar(value=atendimento_dados[1])
        self.entrada_cpf = ttk.Entry(self, textvariable=self.cpf_var, width=50)
        self.entrada_cpf.grid(row=0, column=1, pady=5)

        # Campo Tipo de Pedido
        ttk.Label(self, text="Tipo de Pedido:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.tipo_pedido_var = tk.StringVar(value=atendimento_dados[2])
        self.tipo_pedido_dropdown = ttk.Combobox(self, textvariable=self.tipo_pedido_var, values=[
            "Reclamação de Serviço Público", "Solicitação de Apoio para Saúde", "Pedido de Melhorias no Bairro",
            "Solicitação de Evento Comunitário", "Agradecimento ao Vereador", "Proposta de Projeto para a Comunidade",
            "Solicitação de Atendimento Animal", "Denúncia de Maus-Tratos a Animais"
        ], state="readonly", width=47)
        self.tipo_pedido_dropdown.grid(row=1, column=1, pady=5)

        # Campo Descrição (substituindo Entry por Text para uma área maior)
        ttk.Label(self, text="Descrição:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.descricao_text = tk.Text(self, wrap=tk.WORD, width=50, height=10)
        self.descricao_text.grid(row=2, column=1, pady=5)
        self.descricao_text.insert(tk.END, atendimento_dados[3])

        # Barra de Rolagem para a Descrição
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.descricao_text.yview)
        self.descricao_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=2, sticky="ns")

        # Campo Status
        ttk.Label(self, text="Status:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value=atendimento_dados[6])
        self.status_dropdown = ttk.Combobox(self, textvariable=self.status_var, values=["Pendente", "Em Andamento", "Concluído"], state="readonly", width=47)
        self.status_dropdown.grid(row=3, column=1, pady=5)

        # Botão para Salvar Alterações
        ttk.Button(self, text="Salvar Alterações", command=self.salvar_alteracoes).grid(row=4, column=1, pady=20)

    def salvar_alteracoes(self):
        cpf = self.cpf_var.get()
        tipo_pedido = self.tipo_pedido_var.get()
        descricao = self.descricao_text.get("1.0", tk.END).strip()  # Corrigido: recuperar o texto da caixa de texto
        status = self.status_var.get()

        if tipo_pedido and tipo_pedido != "Selecione o tipo de pedido":
            self.controller.atualizar_atendimento(self.atendimento_id, cpf, tipo_pedido, descricao, status)
            messagebox.showinfo("Sucesso", "Atendimento atualizado com sucesso!")
            self.destroy()
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")

# Tela de Edição de Munícipe
class EditarMunicipeView(tk.Toplevel):
    def __init__(self, parent, controller, municipe_dados):
        super().__init__(parent)
        self.controller = controller
        self.cpf = municipe_dados[0]
        self.title("Editar Munícipe")
        self.geometry("400x400")
        self._construir_interface(municipe_dados)

    def _construir_interface(self, municipe_dados):
        # Campo CPF
        ttk.Label(self, text="CPF:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cpf_var = tk.StringVar(value=municipe_dados[0])
        self.entrada_cpf = ttk.Entry(self, textvariable=self.cpf_var, width=50, state='disabled')
        self.entrada_cpf.grid(row=0, column=1, pady=5)

        # Campo Nome
        ttk.Label(self, text="Nome:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.nome_var = tk.StringVar(value=municipe_dados[1])
        self.entrada_nome = ttk.Entry(self, textvariable=self.nome_var, width=50)
        self.entrada_nome.grid(row=1, column=1, pady=5)

        # Campo Endereço
        ttk.Label(self, text="Endereço:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.endereco_var = tk.StringVar(value=municipe_dados[2])
        self.entrada_endereco = ttk.Entry(self, textvariable=self.endereco_var, width=50)
        self.entrada_endereco.grid(row=2, column=1, pady=5)

        # Campo Telefone
        ttk.Label(self, text="Telefone:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.telefone_var = tk.StringVar(value=municipe_dados[3])
        self.entrada_telefone = ttk.Entry(self, textvariable=self.telefone_var, width=50)
        self.entrada_telefone.grid(row=3, column=1, pady=5)

        # Campo RG
        ttk.Label(self, text="RG:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.rg_var = tk.StringVar(value=municipe_dados[4])
        self.entrada_rg = ttk.Entry(self, textvariable=self.rg_var, width=50)
        self.entrada_rg.grid(row=4, column=1, pady=5)

        # Botão para Salvar Alterações
        ttk.Button(self, text="Salvar Alterações", command=self.salvar_alteracoes).grid(row=5, column=1, pady=20)

    def salvar_alteracoes(self):
        nome = self.nome_var.get()
        endereco = self.endereco_var.get()
        telefone = self.telefone_var.get()
        rg = self.rg_var.get()

        if nome and telefone:
            self.controller.atualizar_municipe(self.cpf, nome, endereco, telefone, rg)
            messagebox.showinfo("Sucesso", "Munícipe atualizado com sucesso!")
            self.destroy()
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")

# Tela de Histórico de Munícipes
class HistoricoMunicipeView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        # Tabela Interativa
        self.treeview = ttk.Treeview(self, columns=("CPF", "Nome", "Endereço", "Telefone", "RG"), show="headings")
        self.treeview.heading("CPF", text="CPF")
        self.treeview.heading("Nome", text="Nome")
        self.treeview.heading("Endereço", text="Endereço")
        self.treeview.heading("Telefone", text="Telefone")
        self.treeview.heading("RG", text="RG")
        self.treeview.pack(fill="both", expand=True)

        # Botões de Ação
        ttk.Button(self, text="Editar Munícipe Selecionado", command=self.editar_municipe).pack(pady=10)
        ttk.Button(self, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).pack(pady=10)

        # Carregar Munícipes
        self.carregar_municipes()

    def carregar_municipes(self):
        municipes = self.controller.consultar_municipes()
        for municipe in municipes:
            self.treeview.insert("", "end", values=municipe)

    def editar_municipe(self):
        try:
            selected_item = self.treeview.selection()[0]
            municipe_data = self.treeview.item(selected_item)['values']
            EditarMunicipeView(self, self.controller, municipe_data)
        except IndexError:
            messagebox.showerror("Erro", "Por favor, selecione um munícipe para editar.")



# Dashboard Principal
class DashboardView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        # Layout principal dividido em duas colunas
        left_frame = ttk.Frame(self, width=200)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        center_frame = ttk.Frame(self)
        center_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Botões no lado esquerdo
        ttk.Button(left_frame, text="Registrar Atendimento", command=lambda: self.switch_view(RegistroAtendimentoView)).pack(fill="x", pady=5)
        ttk.Button(left_frame, text="Registrar Munícipe", command=lambda: self.switch_view(RegistroMunicipeView)).pack(fill="x", pady=5)
        ttk.Button(left_frame, text="Histórico de Atendimentos", command=lambda: self.switch_view(HistoricoAtendimentoView)).pack(fill="x", pady=5)
        ttk.Button(left_frame, text="Histórico de Munícipes", command=lambda: self.switch_view(HistoricoMunicipeView)).pack(fill="x", pady=5)
        ttk.Button(left_frame, text="Gerar Relatório", command=lambda: self.switch_view(RelatorioView)).pack(fill="x", pady=5)
        ttk.Button(left_frame, text="Gerenciar Tarefas", command=lambda: self.switch_view(TarefasView)).pack(fill="x", pady=5)

        # Indicadores de Resumo no Centro (Painéis)
        atendimentos_abertos = ttk.Label(center_frame, text="Atendimentos Abertos: 5", font=("Helvetica", 18), foreground="red")
        atendimentos_abertos.grid(row=0, column=0, pady=5, sticky="n")

        tarefas_pendentes = ttk.Label(center_frame, text="Tarefas Pendentes: 3", font=("Helvetica", 18), foreground="orange")
        tarefas_pendentes.grid(row=1, column=0, pady=5, sticky="n")

        # Histórico de Atendimentos (Tabela Interativa no centro)
        self.treeview = ttk.Treeview(center_frame, columns=("ID", "Nome", "Tipo de Pedido", "Status"), show="headings")
        self.treeview.heading("ID", text="ID")
        self.treeview.heading("Nome", text="Nome")
        self.treeview.heading("Tipo de Pedido", text="Tipo de Pedido")
        self.treeview.heading("Status", text="Status")
        self.treeview.grid(row=2, column=0, pady=10, sticky="nsew")

        # Carregar Atendimentos
        self.carregar_atendimentos()

    def carregar_atendimentos(self):
        atendimentos = self.controller.consultar_atendimentos()
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        for atendimento in atendimentos:
            self.treeview.insert("", "end", values=(atendimento[0], atendimento[7], atendimento[2], atendimento[6]))

# Tela de Relatórios
class RelatorioView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        ttk.Label(self, text="Relatórios").pack()
        ttk.Button(self, text="Gerar Relatório PDF", command=self.gerar_relatorio).pack()
        ttk.Button(self, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).pack(pady=10)

    def gerar_relatorio(self):
        atendimentos = self.controller.consultar_atendimentos()
        self.controller.gerar_relatorio_pdf(atendimentos)
        messagebox.showinfo("Relatório", "Relatório gerado com sucesso.")

# Tela de Gerenciamento de Tarefas (Kanban)
class TarefasView(ttk.Frame):
    def __init__(self, root, controller, switch_view):
        super().__init__(root)
        self.controller = controller
        self.switch_view = switch_view
        self._construir_interface()

    def _construir_interface(self):
        ttk.Label(self, text="Tarefas - Kanban View").pack()
        ttk.Button(self, text="Voltar ao Dashboard", command=lambda: self.switch_view(DashboardView)).pack(pady=10)

# MainApplication - Classe Principal que gerencia a navegação
class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1000x600")
        self.root.title("Sistema de Atendimento ao Gabinete")
        self.model = AtendimentoModel()
        self.controller = AtendimentoController(self.model)
        self.current_view = None
        self.switch_view(DashboardView)

    def switch_view(self, view_class):
        # Remove a view atual e cria a nova view
        if self.current_view is not None:
            self.current_view.pack_forget()
        self.current_view = view_class(self.root, self.controller, self.switch_view)
        self.current_view.pack(fill="both", expand=True)

# Inicialização da Aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
