import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date, timedelta
import math


class CalculadoraNegociacaoMultiNFApp:
    def __init__(self, master):
        self.master = master
        master.title("Calculadora de Negociação de Dívidas (Consistente)")
        master.geometry("1050x830")

        self.lista_nfs_data = []
        self.MAX_PARCELAS_ITER = 120  # Limite para iteração e parcelas
        self.MAX_ITERATION_LOOPS = 10  # Limite para o loop de convergência

        try:
            style = ttk.Style()
            style.configure("TLabel", padding=3, font=('Helvetica', 10))
            style.configure("TEntry", padding=3, font=('Helvetica', 10))
            style.configure("TButton", padding=5, font=('Helvetica', 10))
            style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
            style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))
            style.configure("Total.TLabel", font=('Helvetica', 10, 'bold'))
            style.configure("TRadiobutton", font=('Helvetica', 9))
            style.configure("TCheckbutton", font=('Helvetica', 10))
            style.configure("Accent.TButton", foreground="white", background="navy", font=(
                'Helvetica', 11, 'bold'), padding=5)
            style.map("Accent.TButton",
                      background=[('active', '#0000CD'),
                                   ('pressed', '!disabled', '#000080')],
                      foreground=[('active', 'white')]
                      )
        except tk.TclError as e:
            print(f"Aviso: Não foi possível aplicar estilos ttk. Erro: {e}")

        main_scroll_frame = ttk.Frame(master)
        main_scroll_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(main_scroll_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_main_y = ttk.Scrollbar(
            main_scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_main_y.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar_main_y.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        self.content_frame = ttk.Frame(canvas, padding=(10, 10))
        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        frame_add_nf = ttk.LabelFrame(
            self.content_frame, text="Adicionar Notas Fiscais", padding=(10, 5))
        frame_add_nf.grid(row=0, column=0, padx=5, pady=5,
                          sticky="ew", columnspan=2)
        ttk.Label(frame_add_nf, text="Número NF:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_num_nf = ttk.Entry(frame_add_nf, width=12)
        self.entry_num_nf.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(frame_add_nf, text="Valor Original R$:").grid(
            row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_valor_nf = ttk.Entry(frame_add_nf, width=12)
        self.entry_valor_nf.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ttk.Label(frame_add_nf, text="Vencimento (DD/MM/AAAA):").grid(row=0,
                                                                      column=4, padx=5, pady=5, sticky="w")
        self.entry_venc_nf = ttk.Entry(frame_add_nf, width=12)
        self.entry_venc_nf.grid(row=0, column=5, padx=5, pady=5, sticky="ew")
        self.entry_venc_nf.insert(0, datetime.now().strftime("%d/%m/%Y"))
        btn_add_nf = ttk.Button(
            frame_add_nf, text="[+] Adicionar NF", command=self.adicionar_nf_lista)
        btn_add_nf.grid(row=0, column=6, padx=10, pady=5, sticky="ew")

        cols = ("num_nf", "valor_orig", "venc", "dias_atraso",
                "juros_mora_nf", "multa_nf", "valor_atualizado_nf")
        self.tree_nfs = ttk.Treeview(
            frame_add_nf, columns=cols, show="headings", height=6)
        self.tree_nfs.heading("num_nf", text="Nº NF")
        self.tree_nfs.heading("valor_orig", text="Valor Orig. R$")
        self.tree_nfs.heading("venc", text="Vencimento")
        self.tree_nfs.heading("dias_atraso", text="Dias Atraso")
        self.tree_nfs.heading("juros_mora_nf", text="Juros Mora R$")
        self.tree_nfs.heading("multa_nf", text="Multa R$")
        self.tree_nfs.heading("valor_atualizado_nf", text="Valor Atual. R$")
        for col_name, width in [("num_nf", 70), ("valor_orig", 100), ("venc", 90), ("dias_atraso", 70),
                                ("juros_mora_nf", 110), ("multa_nf", 100), ("valor_atualizado_nf", 120)]:
            anchor_val = "e" if "R$" in self.tree_nfs.heading(col_name)[
                "text"] else "center"
            self.tree_nfs.column(col_name, width=width,
                                 anchor=anchor_val, stretch=tk.YES)
        self.tree_nfs.grid(row=1, column=0, columnspan=7,
                           padx=5, pady=10, sticky="nsew")
        scrollbar_nfs_y = ttk.Scrollbar(
            frame_add_nf, orient="vertical", command=self.tree_nfs.yview)
        self.tree_nfs.configure(yscrollcommand=scrollbar_nfs_y.set)
        scrollbar_nfs_y.grid(row=1, column=7, sticky="ns", pady=10)
        scrollbar_nfs_x = ttk.Scrollbar(
            frame_add_nf, orient="horizontal", command=self.tree_nfs.xview)
        self.tree_nfs.configure(xscrollcommand=scrollbar_nfs_x.set)
        scrollbar_nfs_x.grid(
            row=2, column=0, columnspan=7, sticky="ew", padx=5)
        btn_remove_nf = ttk.Button(
            frame_add_nf, text="[-] Remover NF Selecionada", command=self.remover_nf_selecionada)
        btn_remove_nf.grid(row=3, column=0, columnspan=3,
                           padx=5, pady=5, sticky="w")

        frame_esquerdo = ttk.Frame(self.content_frame)
        frame_esquerdo.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        frame_params_juros = ttk.LabelFrame(
            frame_esquerdo, text="Parâmetros da Negociação e Cálculo de Encargos", padding=(10, 5))
        frame_params_juros.grid(row=0, column=0, padx=5, pady=5, sticky="new")
        self.campos_entrada_negociacao = {}
        param_negociacao_defs = [
            ("Data Base Encargos NF (DD/MM/AAAA):", "data_base_encargos_nf", 0),
            ("Taxa Encargos (% ao Dia - p/ Mora e Parc.):", "taxa_encargos_dia", 1),
            ("% Desconto sobre Juros Mora Totais:",
             "desconto_sobre_juros_mora_totais", 3),
        ]
        for texto, chave, linha in param_negociacao_defs:
            label = ttk.Label(frame_params_juros, text=texto)
            label.grid(row=linha, column=0, padx=5, pady=3, sticky="w")
            entry = ttk.Entry(frame_params_juros, width=25)
            entry.grid(row=linha, column=1, padx=5, pady=3, sticky="ew")
            self.campos_entrada_negociacao[chave] = entry
        self.campos_entrada_negociacao["data_base_encargos_nf"].insert(
            0, datetime.now().strftime("%d/%m/%Y"))
        self.campos_entrada_negociacao["taxa_encargos_dia"].insert(0, "0.40")
        self.campos_entrada_negociacao["desconto_sobre_juros_mora_totais"].insert(
            0, "0")
        self.aplicar_multa_var = tk.BooleanVar(value=False)
        check_multa = ttk.Checkbutton(frame_params_juros, text="Aplicar Multa Contratual (2.014%)",
                                      variable=self.aplicar_multa_var, command=self.atualizar_treeview_nfs_com_calculos)
        check_multa.grid(row=2, column=0, columnspan=2,
                         padx=5, pady=5, sticky="w")

        frame_cond_pag = ttk.LabelFrame(
            frame_esquerdo, text="Condições de Pagamento", padding=(10, 5))
        frame_cond_pag.grid(row=1, column=0, padx=5, pady=5, sticky="new")
        self.campos_entrada_pagamento = {}
        ttk.Label(frame_cond_pag, text="Forma de Pagamento:").grid(
            row=0, column=0, padx=5, pady=3, sticky="w")
        self.combo_forma_pagamento = ttk.Combobox(
            frame_cond_pag, values=["À Vista", "Parcelado"], state="readonly", width=23)
        self.combo_forma_pagamento.grid(
            row=0, column=1, padx=5, pady=3, sticky="ew")
        self.combo_forma_pagamento.current(0)
        self.combo_forma_pagamento.bind(
            "<<ComboboxSelected>>", self.toggle_parcelamento_fields)
        ttk.Label(frame_cond_pag, text="Data do 1º Pagamento (DD/MM/AAAA):").grid(
            row=1, column=0, padx=5, pady=3, sticky="w")
        self.entry_data_primeiro_pagamento = ttk.Entry(
            frame_cond_pag, width=25)
        self.entry_data_primeiro_pagamento.grid(
            row=1, column=1, padx=5, pady=3, sticky="ew")
        self.entry_data_primeiro_pagamento.insert(
            0, (datetime.now() + timedelta(days=15)).strftime("%d/%m/%Y"))
        ttk.Label(frame_cond_pag, text="Frequência de Pagamento:").grid(
            row=2, column=0, padx=5, pady=3, sticky="w")
        self.combo_frequencia_pagamento = ttk.Combobox(
            frame_cond_pag, values=["Semanal", "Quinzenal"], state="readonly", width=23)
        self.combo_frequencia_pagamento.grid(
            row=2, column=1, padx=5, pady=3, sticky="ew")
        self.combo_frequencia_pagamento.current(1)
        self.tipo_calculo_parcela_var = tk.StringVar(value="por_valor")
        ttk.Label(frame_cond_pag, text="Calcular parcelamento por:").grid(
            row=3, column=0, padx=5, pady=3, sticky="w")
        self.frame_radio_tipo_parcela = ttk.Frame(frame_cond_pag)
        self.frame_radio_tipo_parcela.grid(
            row=3, column=1, padx=5, pady=0, sticky="ew")
        ttk.Radiobutton(self.frame_radio_tipo_parcela, text="Valor da Parcela", variable=self.tipo_calculo_parcela_var,
                        value="por_valor", command=self.toggle_parcelamento_fields).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(self.frame_radio_tipo_parcela, text="Nº de Parcelas", variable=self.tipo_calculo_parcela_var,
                        value="por_numero", command=self.toggle_parcelamento_fields).pack(side=tk.LEFT, padx=2)

        param_pagamento_defs = [
            ("Valor Desejado da Parcela R$ (Aprox.):",
             "valor_desejado_parcela_aprox", 4),
            ("Número de Parcelas Desejado:", "numero_parcelas_desejado", 5),
        ]
        for texto, chave, linha in param_pagamento_defs:
            label = ttk.Label(frame_cond_pag, text=texto)
            label.grid(row=linha, column=0, padx=5, pady=3, sticky="w")
            entry = ttk.Entry(frame_cond_pag, width=25)
            entry.grid(row=linha, column=1, padx=5, pady=3, sticky="ew")
            self.campos_entrada_pagamento[chave] = entry
            self.campos_entrada_pagamento[chave + "_label"] = label
        self.campos_entrada_pagamento["valor_desejado_parcela_aprox"].insert(
            0, "100.00")
        self.campos_entrada_pagamento["numero_parcelas_desejado"].insert(
            0, "3")

        btn_calcular = ttk.Button(frame_esquerdo, text="Calcular Negociação",
                                  command=self.calcular_negociacao_final, style="Accent.TButton")
        btn_calcular.grid(row=2, column=0, padx=10, pady=15, sticky="ew")
        btn_texto_copiavel = ttk.Button(
            frame_esquerdo, text="Gerar Texto para Copiar", command=self.gerar_texto_copiavel)
        btn_texto_copiavel.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        frame_resultados = ttk.LabelFrame(
            self.content_frame, text="Resultados da Negociação", padding=(10, 5))
        frame_resultados.grid(row=1, column=1, rowspan=3,
                              padx=5, pady=5, sticky="nsew")
        self.labels_resultados = {}
        nomes_resultados = [
            ("Total Principal Original (NFs): R$", "total_principal_original"),
            ("Total Juros de Mora Calculados: R$", "total_juros_mora"),
            ("Total Multas Aplicadas: R$", "total_multas_aplicadas"),
            ("SALDO DEVEDOR (Principal+Juros+Multa): R$", "saldo_devedor_base", True),
            ("Desconto nos Juros: R$", "desconto_juros"),
            ("Juros do Parcelamento (Data Média): R$",
             "juros_parcelamento_data_media"),
            ("VALOR TOTAL A PAGAR (Com Juros Parc.): R$",
             "valor_total_a_pagar_final", True),
            ("--- Pagamento À Vista ---", None, True),
            ("Valor da Parcela Única: R$", "parcela_unica_avista"),
            ("--- Pagamento Parcelado ---", None, True),
            ("Número de Parcelas:", "num_parcelas_final"),
            ("Valor de Cada Parcela: R$", "valor_cada_parcela_final"),
            ("Valor Total Parcelado: R$", "total_pago_parcelamento", True),
            ("Datas das Parcelas:", "datas_parcelas_display", False, True)
        ]
        current_row = 0
        self.text_datas_parcelas = None
        for texto, chave, *opts in nomes_resultados:
            is_bold = opts[0] if len(opts) > 0 else False
            is_multiline = opts[1] if len(opts) > 1 else False
            lbl_style = "Total.TLabel" if is_bold else "TLabel"
            label_nome = ttk.Label(
                frame_resultados, text=texto, style=lbl_style)
            label_nome.grid(row=current_row, column=0, padx=5, pady=2,
                            sticky="nw" if is_multiline else "w", columnspan=2 if not chave else 1)
            if chave:
                if is_multiline:
                    self.text_datas_parcelas = tk.Text(frame_resultados, height=4, width=30, wrap=tk.WORD, font=(
                        'Helvetica', 9), relief=tk.SOLID, borderwidth=1)
                    self.text_datas_parcelas.grid(
                        row=current_row, column=1, padx=5, pady=2, sticky="ew")
                    self.text_datas_parcelas.config(state=tk.DISABLED)
                    self.labels_resultados[chave] = self.text_datas_parcelas
                else:
                    label_valor = ttk.Label(
                        frame_resultados, text="0.00" if "R$" in texto else "0", style=lbl_style)
                    label_valor.grid(row=current_row, column=1,
                                     padx=5, pady=2, sticky="w")
                    self.labels_resultados[chave] = label_valor
            current_row += 1

        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=2)
        self.toggle_parcelamento_fields()

    def get_float(self, entry_widget_or_str, default_value=0.0):
        val = entry_widget_or_str.get() if hasattr(
            entry_widget_or_str, 'get') else str(entry_widget_or_str)
        try:
            return float(val.replace(",", "."))
        except ValueError:
            return default_value

    def get_int(self, entry_widget, default_value=0):
        try:
            return int(entry_widget.get())
        except ValueError:
            return default_value

    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            return None

    def date_to_str(self, date_obj):
        """Convert date object to string for JSON serialization"""
        if isinstance(date_obj, date):
            return date_obj.strftime("%d/%m/%Y")
        return str(date_obj)

    def serialize_nf_data(self, nf_data):
        """Serialize NF data to be JSON compatible"""
        serialized = nf_data.copy()
        if 'data_vencimento' in serialized:
            serialized['data_vencimento'] = self.date_to_str(serialized['data_vencimento'])
        return serialized

    def adicionar_nf_lista(self):
        num_nf = self.entry_num_nf.get()
        valor_original = self.get_float(self.entry_valor_nf)
        venc_str = self.entry_venc_nf.get()
        data_venc = self.parse_date(venc_str)
        if not num_nf or valor_original <= 0 or not data_venc:
            messagebox.showerror(
                "Erro de Entrada", "Preencha Nº NF, Valor Original (>0) e Vencimento (DD/MM/AAAA) corretamente.")
            return
        self.lista_nfs_data.append({"num_nf": num_nf, "valor_original": valor_original,
                                   "data_vencimento": data_venc, "venc_str": venc_str})
        self.atualizar_treeview_nfs_com_calculos()
        self.entry_num_nf.delete(0, tk.END)
        self.entry_valor_nf.delete(0, tk.END)
        self.entry_num_nf.focus()

    def remover_nf_selecionada(self):
        selected_item = self.tree_nfs.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Nenhuma NF selecionada.")
            return
        selected_iid = selected_item[0]
        nf_num_para_remover = self.tree_nfs.item(selected_iid)['values'][0]
        self.lista_nfs_data = [nf for nf in self.lista_nfs_data if str(
            nf["num_nf"]) != str(nf_num_para_remover)]
        self.tree_nfs.delete(selected_iid)
        self.atualizar_treeview_nfs_com_calculos()

    def atualizar_treeview_nfs_com_calculos(self):
        for i in self.tree_nfs.get_children():
            self.tree_nfs.delete(i)
        data_base_encargos_str = self.campos_entrada_negociacao["data_base_encargos_nf"].get(
        )
        taxa_encargos_dia_str = self.campos_entrada_negociacao["taxa_encargos_dia"].get(
        )
        aplica_multa = self.aplicar_multa_var.get()
        data_base_encargos = self.parse_date(data_base_encargos_str)
        taxa_encargos_dia_decimal = self.get_float(
            taxa_encargos_dia_str) / 100.0

        for nf_data in self.lista_nfs_data:
            dias_atraso, juros_mora_nf_total, multa_nf = 0, 0.0, 0.0
            if data_base_encargos and nf_data["data_vencimento"] < data_base_encargos:
                dias_atraso = (data_base_encargos -
                               nf_data["data_vencimento"]).days
                if dias_atraso > 0 and taxa_encargos_dia_decimal > 0:
                    juros_diario_valor = nf_data["valor_original"] * \
                        taxa_encargos_dia_decimal
                    juros_diario_arredondado = round(juros_diario_valor, 2)
                    juros_mora_nf_total = dias_atraso * juros_diario_arredondado
                elif dias_atraso <= 0:
                    dias_atraso = 0

            if aplica_multa:
                multa_nf = nf_data["valor_original"] * 0.02014
            nf_data.update({'dias_atraso': dias_atraso, 'juros_mora_calculado': juros_mora_nf_total, 'multa_calculada': multa_nf,
                            'valor_atualizado_calculado': nf_data['valor_original'] + juros_mora_nf_total + multa_nf})
            self.tree_nfs.insert("", "end", values=(
                nf_data["num_nf"], f"{nf_data['valor_original']:.2f}", nf_data["venc_str"],
                dias_atraso, f"{juros_mora_nf_total:.2f}", f"{multa_nf:.2f}", f"{nf_data['valor_atualizado_calculado']:.2f}"
            ))

    def toggle_parcelamento_fields(self, event=None):
        opcao_pagamento = self.combo_forma_pagamento.get()
        tipo_calculo_parcela = self.tipo_calculo_parcela_var.get()
        estado_geral_parcelamento = "normal" if opcao_pagamento == "Parcelado" else "disabled"

        self.entry_data_primeiro_pagamento.config(
            state=estado_geral_parcelamento)
        self.combo_frequencia_pagamento.config(state=estado_geral_parcelamento)

        if hasattr(self, 'frame_radio_tipo_parcela'):
            for radio_button in self.frame_radio_tipo_parcela.winfo_children():
                if isinstance(radio_button, ttk.Radiobutton):
                    radio_button.config(state=estado_geral_parcelamento)

        if opcao_pagamento == "Parcelado":
            if tipo_calculo_parcela == "por_valor":
                self.campos_entrada_pagamento["valor_desejado_parcela_aprox"].config(
                    state="normal")
                self.campos_entrada_pagamento["valor_desejado_parcela_aprox_label"].config(
                    state="normal")
                self.campos_entrada_pagamento["numero_parcelas_desejado"].config(
                    state="disabled")
                self.campos_entrada_pagamento["numero_parcelas_desejado_label"].config(
                    state="disabled")
            elif tipo_calculo_parcela == "por_numero":
                self.campos_entrada_pagamento["valor_desejado_parcela_aprox"].config(
                    state="disabled")
                self.campos_entrada_pagamento["valor_desejado_parcela_aprox_label"].config(
                    state="disabled")
                self.campos_entrada_pagamento["numero_parcelas_desejado"].config(
                    state="normal")
                self.campos_entrada_pagamento["numero_parcelas_desejado_label"].config(
                    state="normal")
        else:
            self.campos_entrada_pagamento["valor_desejado_parcela_aprox"].config(
                state="disabled")
            self.campos_entrada_pagamento["valor_desejado_parcela_aprox_label"].config(
                state="disabled")
            self.campos_entrada_pagamento["numero_parcelas_desejado"].config(
                state="disabled")
            self.campos_entrada_pagamento["numero_parcelas_desejado_label"].config(
                state="disabled")

    def calcular_parcela_base_n(self, valor_total_a_financiar, num_parcelas):
        if num_parcelas <= 0 or valor_total_a_financiar < 0:
            return 0
        return valor_total_a_financiar / num_parcelas if num_parcelas > 0 else 0

    def calcular_n_base_valor_parcela_desejada(self, valor_total_a_financiar, valor_parcela_desejada):
        if valor_total_a_financiar <= 0:
            return 0, 0
        if valor_parcela_desejada <= 0:
            return self.MAX_PARCELAS_ITER, self.calcular_parcela_base_n(valor_total_a_financiar, self.MAX_PARCELAS_ITER)

        num_p = math.ceil(valor_total_a_financiar / valor_parcela_desejada)
        if num_p == 0 and valor_total_a_financiar > 0:
            num_p = 1
        if num_p > self.MAX_PARCELAS_ITER:
            num_p = self.MAX_PARCELAS_ITER

        valor_real_parcela = self.calcular_parcela_base_n(
            valor_total_a_financiar, num_p)
        return int(round(num_p)), valor_real_parcela

    def _calculate_financing_details_for_N(self, saldo_base, num_parcelas_para_data_media, data_primeiro_pag, frequencia, taxa_diaria_decimal):
        """Helper to calculate financing interest and new total based on N for data_media."""
        if num_parcelas_para_data_media <= 0:
            return 0.0, saldo_base

        datas_parcelas = self.gerar_datas_parcelas(
            data_primeiro_pag, num_parcelas_para_data_media, frequencia)
        if not datas_parcelas:
            return 0.0, saldo_base

        idx_data_media = math.ceil(num_parcelas_para_data_media / 2.0) - 1
        idx_data_media = max(0, min(idx_data_media, len(datas_parcelas) - 1))
        data_media = datas_parcelas[idx_data_media]

        juros_financiamento = 0.0
        if data_media > data_primeiro_pag and taxa_diaria_decimal > 0:
            dias_fin = (data_media - data_primeiro_pag).days
            if dias_fin > 0:
                juros_financiamento = saldo_base * taxa_diaria_decimal * dias_fin

        valor_total_com_juros_fin = saldo_base + juros_financiamento
        return juros_financiamento, valor_total_com_juros_fin

    def gerar_datas_parcelas(self, data_inicio, num_parcelas, frequencia):
        datas = []
        if not data_inicio or num_parcelas <= 0:
            return datas
        data_atual = data_inicio
        delta_days = 7 if frequencia == "Semanal" else 15
        for _ in range(int(round(num_parcelas))):
            datas.append(data_atual)
            data_atual += timedelta(days=delta_days)
        return datas

    def calcular_negociacao_final(self):
        self.atualizar_treeview_nfs_com_calculos()
        if not self.lista_nfs_data:
            messagebox.showwarning("Atenção", "Nenhuma NF adicionada.")
            return

        data_base_encargos_nf_str = self.campos_entrada_negociacao["data_base_encargos_nf"].get(
        )
        data_base_encargos_nf = self.parse_date(data_base_encargos_nf_str)
        if not data_base_encargos_nf:
            messagebox.showerror("Erro", "Data Base Encargos NF inválida.")
            return

        taxa_encargos_dia_decimal = self.get_float(
            self.campos_entrada_negociacao["taxa_encargos_dia"].get()) / 100.0

        total_principal = sum(nf['valor_original']
                              for nf in self.lista_nfs_data)
        total_juros_mora = sum(nf.get('juros_mora_calculado', 0.0)
                               for nf in self.lista_nfs_data)
        total_multas = sum(nf.get('multa_calculada', 0.0)
                           for nf in self.lista_nfs_data)
        saldo_devedor_antes_desconto = total_principal + total_juros_mora + total_multas

        perc_desc_juros = self.get_float(
            self.campos_entrada_negociacao["desconto_sobre_juros_mora_totais"]) / 100.0
        valor_desc_juros = total_juros_mora * perc_desc_juros
        saldo_liquido_para_pagamento_base = saldo_devedor_antes_desconto - valor_desc_juros
        if saldo_liquido_para_pagamento_base < 0:
            saldo_liquido_para_pagamento_base = 0.0

        self.labels_resultados["total_principal_original"].config(
            text=f"{total_principal:.2f}")
        self.labels_resultados["total_juros_mora"].config(
            text=f"{total_juros_mora:.2f}")
        self.labels_resultados["total_multas_aplicadas"].config(
            text=f"{total_multas:.2f}")
        self.labels_resultados["saldo_devedor_base"].config(
            text=f"{saldo_devedor_antes_desconto:.2f}")
        self.labels_resultados["desconto_juros"].config(
            text=f"{valor_desc_juros:.2f}")

        self.labels_resultados["juros_parcelamento_data_media"].config(
            text="0.00")
        self.labels_resultados["valor_total_a_pagar_final"].config(
            text=f"{saldo_liquido_para_pagamento_base:.2f}")
        self.labels_resultados["parcela_unica_avista"].config(text="0.00")
        self.labels_resultados["num_parcelas_final"].config(text="0")
        self.labels_resultados["valor_cada_parcela_final"].config(text="0.00")
        self.labels_resultados["total_pago_parcelamento"].config(text="0.00")
        if self.text_datas_parcelas:
            self.text_datas_parcelas.config(state=tk.NORMAL)
            self.text_datas_parcelas.delete(1.0, tk.END)
            self.text_datas_parcelas.config(state=tk.DISABLED)

        self.current_negotiation_details = {
            "tipo_pagamento": self.combo_forma_pagamento.get(), "nfs": self.lista_nfs_data,
            "total_principal": total_principal, "total_juros_mora": total_juros_mora,
            "total_multas": total_multas, "desconto_juros_valor": valor_desc_juros,
            "saldo_devedor_base_apos_desconto": saldo_liquido_para_pagamento_base,
            "parcelas_info": [], "juros_financiamento_data_media": "0.00",
            "valor_total_final_com_juros_parcelamento": f"{saldo_liquido_para_pagamento_base:.2f}"
        }

        if self.combo_forma_pagamento.get() == "À Vista":
            self.labels_resultados["parcela_unica_avista"].config(
                text=f"{saldo_liquido_para_pagamento_base:.2f}")
            self.labels_resultados["valor_total_a_pagar_final"].config(
                text=f"{saldo_liquido_para_pagamento_base:.2f}")
            self.current_negotiation_details[
                "valor_total_final_com_juros_parcelamento"] = f"{saldo_liquido_para_pagamento_base:.2f}"

        else:  # Parcelado
            if saldo_liquido_para_pagamento_base <= 0:
                return

            data_primeiro_pag_str = self.entry_data_primeiro_pagamento.get()
            data_primeiro_pag = self.parse_date(data_primeiro_pag_str)
            if not data_primeiro_pag:
                messagebox.showerror("Erro Parcelamento",
                                     "Data do 1º Pagamento inválida.")
                return

            frequencia = self.combo_frequencia_pagamento.get()
            tipo_calculo_parcela = self.tipo_calculo_parcela_var.get()

            num_p_final_calc, val_p_final_calc, juros_financiamento_calc = 0, 0.0, 0.0
            # valor_total_final_a_parcelar_calc = saldo_liquido_para_pagamento_base # Este será atualizado

            if tipo_calculo_parcela == "por_valor":
                valor_desejado_parc = self.get_float(
                    self.campos_entrada_pagamento["valor_desejado_parcela_aprox"].get())
                if valor_desejado_parc <= 0 and saldo_liquido_para_pagamento_base > 0:
                    messagebox.showerror(
                        "Erro Parcelamento", "Valor Desejado da Parcela deve ser positivo.")
                    return

                N_iter = self.calcular_n_base_valor_parcela_desejada(
                    saldo_liquido_para_pagamento_base, valor_desejado_parc)[0]
                if N_iter == 0 and saldo_liquido_para_pagamento_base > 0:
                    N_iter = 1
                N_iter = min(N_iter, self.MAX_PARCELAS_ITER)

                current_juros_financiamento = 0.0
                current_valor_total_iter = saldo_liquido_para_pagamento_base

                for i in range(self.MAX_ITERATION_LOOPS):
                    if N_iter <= 0:
                        N_iter = 1

                    iter_juros, iter_total_com_juros = self._calculate_financing_details_for_N(
                        saldo_liquido_para_pagamento_base, N_iter, data_primeiro_pag, frequencia, taxa_encargos_dia_decimal
                    )

                    N_novo_iter, _ = self.calcular_n_base_valor_parcela_desejada(
                        iter_total_com_juros, valor_desejado_parc)
                    if N_novo_iter == 0 and iter_total_com_juros > 0:
                        N_novo_iter = 1
                    N_novo_iter = min(N_novo_iter, self.MAX_PARCELAS_ITER)

                    # Store current iteration's results before checking for convergence or changing N_iter
                    current_juros_financiamento = iter_juros
                    current_valor_total_iter = iter_total_com_juros

                    if N_novo_iter == N_iter:
                        num_p_final_calc = N_iter
                        juros_financiamento_calc = current_juros_financiamento
                        valor_total_final_a_parcelar_calc = current_valor_total_iter
                        val_p_final_calc = self.calcular_parcela_base_n(
                            valor_total_final_a_parcelar_calc, num_p_final_calc)
                        break
                    N_iter = N_novo_iter
                else:  # Loop finished without break
                    num_p_final_calc = N_iter
                    juros_financiamento_calc = current_juros_financiamento
                    valor_total_final_a_parcelar_calc = current_valor_total_iter
                    val_p_final_calc = self.calcular_parcela_base_n(
                        valor_total_final_a_parcelar_calc, num_p_final_calc)

            elif tipo_calculo_parcela == "por_numero":
                num_p_desejado = self.get_int(
                    self.campos_entrada_pagamento["numero_parcelas_desejado"])
                if num_p_desejado <= 0 and saldo_liquido_para_pagamento_base > 0:
                    messagebox.showerror(
                        "Erro Parcelamento", "Número de Parcelas Desejado deve ser positivo.")
                    return
                num_p_final_calc = num_p_desejado

                juros_financiamento_calc, valor_total_final_a_parcelar_calc = \
                    self._calculate_financing_details_for_N(
                        saldo_liquido_para_pagamento_base, num_p_final_calc, data_primeiro_pag, frequencia, taxa_encargos_dia_decimal
                    )
                val_p_final_calc = self.calcular_parcela_base_n(
                    valor_total_final_a_parcelar_calc, num_p_final_calc)

            if num_p_final_calc > 0 and val_p_final_calc > 0 and val_p_final_calc != float('inf'):
                total_pago_parc = val_p_final_calc * num_p_final_calc
                self.labels_resultados["juros_parcelamento_data_media"].config(
                    text=f"{juros_financiamento_calc:.2f}")
                self.labels_resultados["valor_total_a_pagar_final"].config(
                    text=f"{valor_total_final_a_parcelar_calc:.2f}")
                self.labels_resultados["num_parcelas_final"].config(
                    text=str(int(round(num_p_final_calc))))
                self.labels_resultados["valor_cada_parcela_final"].config(
                    text=f"{val_p_final_calc:.2f}")
                self.labels_resultados["total_pago_parcelamento"].config(
                    text=f"{total_pago_parc:.2f}")

                datas_str = ""
                self.current_negotiation_details["parcelas_info"] = []
                datas_efetivas_parcelas = self.gerar_datas_parcelas(
                    data_primeiro_pag, int(round(num_p_final_calc)), frequencia)
                for i, dt_parcela in enumerate(datas_efetivas_parcelas):
                    parcela_info = {"data": dt_parcela.strftime(
                        "%d/%m/%Y"), "valor": val_p_final_calc}
                    self.current_negotiation_details["parcelas_info"].append(
                        parcela_info)
                    datas_str += f"{i+1}ª: {parcela_info['data']} - R$ {parcela_info['valor']:.2f}\n"

                if self.text_datas_parcelas:
                    self.text_datas_parcelas.config(state=tk.NORMAL)
                    self.text_datas_parcelas.delete(1.0, tk.END)
                    self.text_datas_parcelas.insert(tk.END, datas_str.strip())
                    self.text_datas_parcelas.config(state=tk.DISABLED)

                self.current_negotiation_details[
                    "juros_financiamento_data_media"] = f"{juros_financiamento_calc:.2f}"
                self.current_negotiation_details[
                    "valor_total_final_com_juros_parcelamento"] = f"{valor_total_final_a_parcelar_calc:.2f}"
                self.current_negotiation_details["num_parcelas_final"] = str(
                    int(round(num_p_final_calc)))
                self.current_negotiation_details[
                    "valor_parcela_final"] = f"{val_p_final_calc:.2f}"
                self.current_negotiation_details[
                    "total_final_parcelado"] = f"{total_pago_parc:.2f}"
            else:
                if saldo_liquido_para_pagamento_base > 0:
                    messagebox.showinfo("Info Parcelamento",
                                        "Não foi possível calcular o parcelamento com os valores fornecidos.\n"
                                        "Verifique se os dados do parcelamento são viáveis.")

    def gerar_texto_copiavel(self):
        if not hasattr(self, 'current_negotiation_details') or not self.current_negotiation_details.get("nfs"):
            messagebox.showinfo(
                "Info", "Calcule uma negociação primeiro para gerar o texto.")
            return

        details = self.current_negotiation_details
        texto_final = []
        aplica_multa = self.aplicar_multa_var.get()

        # Feedback inicial - mostrar todas as NFs e seus valores originais
        texto_final.append("RESUMO DAS NOTAS FISCAIS EM NEGOCIAÇÃO:")
        for nf in details["nfs"]:
            texto_final.append(f"NF: {nf['num_nf']} - Valor da Fatura: R$ {nf['valor_original']:.2f}")
        texto_final.append("")  # Linha em branco para separar
        texto_final.append("=" * 50)
        texto_final.append("")

        if details["tipo_pagamento"] == "À Vista":
            if len(details["nfs"]) == 1:
                nf = details["nfs"][0]
                texto_final.append("Pagamento à vista de apenas um título:")
                texto_final.append(f"NF: {nf['num_nf']}")
                texto_final.append(
                    f"Valor Original: R$ {nf['valor_original']:.2f}")
                texto_final.append(
                    f"Juros Mora: R$ {nf.get('juros_mora_calculado', 0.0):.2f}")
                if aplica_multa and nf.get('multa_calculada', 0.0) > 0:
                    texto_final.append(
                        f"Multa: R$ {nf.get('multa_calculada', 0.0):.2f}")
                if float(details['desconto_juros_valor']) > 0:
                    texto_final.append(
                        f"Desconto Juros Mora: R$ {details['desconto_juros_valor']:.2f}")
                texto_final.append(
                    f"VALOR FINAL PARA PAGAMENTO À VISTA: R$ {float(details['saldo_devedor_base_apos_desconto']):.2f}")
            else:
                texto_final.append("Pagamento à vista de vários títulos:")
                for nf in details["nfs"]:
                    valor_nf_atualizado = nf.get(
                        'valor_atualizado_calculado', nf['valor_original'])
                    texto_final.append(
                        f"NF: {nf['num_nf']} - Valor Atualizado (c/ encargos da NF): R$ {valor_nf_atualizado:.2f}")
                texto_final.append("---")
                texto_final.append(
                    f"Total Principal Original: R$ {details['total_principal']:.2f}")
                texto_final.append(
                    f"Total Juros Mora: R$ {details['total_juros_mora']:.2f}")
                if aplica_multa and float(details['total_multas']) > 0:
                    texto_final.append(
                        f"Total Multas Aplicadas: R$ {details['total_multas']:.2f}")
                texto_final.append(
                    f"Saldo Devedor Bruto: R$ {float(details['total_principal']) + float(details['total_juros_mora']) + float(details['total_multas']):.2f}")
                if float(details['desconto_juros_valor']) > 0:
                    texto_final.append(
                        f"Desconto Total Juros Mora: R$ {details['desconto_juros_valor']:.2f}")
                texto_final.append(
                    f"VALOR TOTAL PARA PAGAMENTO À VISTA: R$ {float(details['saldo_devedor_base_apos_desconto']):.2f}")

        elif details["tipo_pagamento"] == "Parcelado":
            texto_final.append("Pagamento parcelado:")
            for nf in details["nfs"]:
                valor_nf_atualizado = nf.get(
                    'valor_atualizado_calculado', nf['valor_original'])
                texto_final.append(
                    f"NF: {nf['num_nf']} - Valor Atualizado (c/ encargos da NF): R$ {valor_nf_atualizado:.2f}")
            texto_final.append("---")
            texto_final.append(
                f"Saldo Devedor Base (após descontos de mora): R$ {float(details['saldo_devedor_base_apos_desconto']):.2f}")
            texto_final.append(
                f"Juros do Parcelamento (Data Média): R$ {details.get('juros_financiamento_data_media', '0.00')}")
            texto_final.append(
                f"VALOR TOTAL A PARCELAR (COM JUROS DO PARCELAMENTO): R$ {details.get('valor_total_final_com_juros_parcelamento', '0.00')}")
            texto_final.append("---")

            if details.get("parcelas_info"):
                for i, p_info in enumerate(details["parcelas_info"]):
                    texto_final.append(
                        f"{i+1}° Pagamento dia {p_info['data']} - R$ {p_info['valor']:.2f}")
            else:
                texto_final.append(
                    f"{details.get('num_parcelas_final', 'N/A')} parcelas de R$ {details.get('valor_parcela_final', 'N/A')}")

            texto_final.append(
                f"Total Final Parcelado: R$ {details.get('total_final_parcelado', 'N/A')}")

        top = tk.Toplevel(self.master)
        top.title("Texto para Copiar")
        top.geometry("550x450")

        text_widget = tk.Text(top, wrap=tk.WORD, font=(
            'Courier New', 10), padx=5, pady=5)
        text_widget.pack(expand=True, fill=tk.BOTH)
        text_widget.insert(tk.END, "\n".join(texto_final))
        text_widget.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(top)
        btn_frame.pack(pady=5)

        def copy_to_clipboard():
            self.master.clipboard_clear()
            self.master.clipboard_append(text_widget.get(1.0, tk.END))
            messagebox.showinfo(
                "Copiado", "Texto copiado para a área de transferência!", parent=top)

        copy_btn = ttk.Button(btn_frame, text="Copiar Tudo",
                              command=copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=5)
        close_btn = ttk.Button(btn_frame, text="Fechar", command=top.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)

        top.transient(self.master)
        top.grab_set()
        self.master.wait_window(top)


if __name__ == '__main__':
    root = tk.Tk()
    app = CalculadoraNegociacaoMultiNFApp(root)
    root.mainloop()
