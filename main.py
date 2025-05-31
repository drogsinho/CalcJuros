import webview
import json
from datetime import datetime, date, timedelta
import math


class CalculadoraAPI:
    def __init__(self):
        self.lista_nfs_data = []
        self.MAX_PARCELAS_ITER = 120
        self.MAX_ITERATION_LOOPS = 10
        self.current_negotiation_details = {}

    def get_float(self, value, default_value=0.0):
        try:
            return float(str(value).replace(",", "."))
        except (ValueError, TypeError):
            return default_value

    def get_int(self, value, default_value=0):
        try:
            return int(value)
        except (ValueError, TypeError):
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

    def adicionar_nf(self, num_nf, valor_original, venc_str):
        valor_original = self.get_float(valor_original)
        data_venc = self.parse_date(venc_str)
        
        if not num_nf or valor_original <= 0 or not data_venc:
            return {"success": False, "message": "Preencha todos os campos corretamente"}
        
        self.lista_nfs_data.append({
            "num_nf": num_nf,
            "valor_original": valor_original,
            "data_vencimento": data_venc,
            "venc_str": venc_str
        })
        
        return {"success": True, "nfs": self.get_nfs_calculadas()}

    def remover_nf(self, num_nf):
        self.lista_nfs_data = [nf for nf in self.lista_nfs_data if str(nf["num_nf"]) != str(num_nf)]
        return {"success": True, "nfs": self.get_nfs_calculadas()}

    def get_nfs_calculadas(self):
        return [self.calcular_nf_encargos(nf) for nf in self.lista_nfs_data]

    def calcular_nf_encargos(self, nf_data, data_base_str="", taxa_dia_str="0.40", aplica_multa=False):
        data_base = self.parse_date(data_base_str) if data_base_str else datetime.now().date()
        taxa_dia_decimal = self.get_float(taxa_dia_str) / 100.0
        
        dias_atraso = 0
        juros_mora = 0.0
        multa = 0.0
        
        if data_base and nf_data["data_vencimento"] < data_base:
            dias_atraso = (data_base - nf_data["data_vencimento"]).days
            if dias_atraso > 0 and taxa_dia_decimal > 0:
                juros_diario = nf_data["valor_original"] * taxa_dia_decimal
                juros_mora = dias_atraso * round(juros_diario, 2)
        
        if aplica_multa:
            multa = nf_data["valor_original"] * 0.02014
        
        valor_atualizado = nf_data["valor_original"] + juros_mora + multa
        
        # Return JSON serializable data
        return {
            "num_nf": nf_data["num_nf"],
            "valor_original": nf_data["valor_original"],
            "venc_str": nf_data["venc_str"],
            "dias_atraso": dias_atraso,
            "juros_mora": juros_mora,
            "multa": multa,
            "valor_atualizado": valor_atualizado,
            "juros_mora_calculado": juros_mora,
            "multa_calculada": multa,
            "valor_atualizado_calculado": valor_atualizado
        }

    def calcular_negociacao(self, params):
        if not self.lista_nfs_data:
            return {"success": False, "message": "Nenhuma NF adicionada"}
        
        data_base = params.get("data_base_encargos", datetime.now().strftime("%d/%m/%Y"))
        taxa_dia = params.get("taxa_encargos_dia", "0.40")
        aplica_multa = params.get("aplicar_multa", False)
        desconto_juros_perc = self.get_float(params.get("desconto_juros", "0"))
        
        # Calcular totais
        nfs_calculadas = [self.calcular_nf_encargos(nf, data_base, taxa_dia, aplica_multa) for nf in self.lista_nfs_data]
        
        total_principal = sum(nf["valor_original"] for nf in nfs_calculadas)
        total_juros = sum(nf["juros_mora"] for nf in nfs_calculadas)
        total_multas = sum(nf["multa"] for nf in nfs_calculadas)
        
        desconto_juros = total_juros * (desconto_juros_perc / 100.0)
        saldo_base = total_principal + total_juros + total_multas - desconto_juros
        
        resultado = {
            "success": True,
            "nfs_calculadas": nfs_calculadas,
            "total_principal": total_principal,
            "total_juros": total_juros,
            "total_multas": total_multas,
            "desconto_juros": desconto_juros,
            "saldo_base": saldo_base,
            "parcelas_info": []
        }
        
        # Calcular parcelamento se necessário
        if params.get("forma_pagamento") == "parcelado":
            resultado.update(self._calcular_parcelamento(params, saldo_base))
        
        # Store current details for text generation (matching Tkinter format)
        self.current_negotiation_details = {
            "tipo_pagamento": params.get("forma_pagamento", "avista"),
            "nfs": nfs_calculadas,
            "total_principal": total_principal,
            "total_juros_mora": total_juros,
            "total_multas": total_multas,
            "desconto_juros_valor": desconto_juros,
            "saldo_devedor_base_apos_desconto": saldo_base,
            "parcelas_info": resultado.get("parcelas_info", []),
            "juros_financiamento_data_media": f"{resultado.get('juros_parcelamento', 0):.2f}",
            "valor_total_final_com_juros_parcelamento": f"{resultado.get('valor_total_parcelado', saldo_base):.2f}",
            "num_parcelas_final": str(resultado.get('num_parcelas', 0)),
            "valor_parcela_final": f"{resultado.get('valor_cada_parcela', 0):.2f}",
            "total_final_parcelado": f"{resultado.get('valor_total_parcelado', 0):.2f}"
        }
        
        return resultado

    def _calcular_parcelamento(self, params, saldo_base):
        data_primeiro_pag = self.parse_date(params.get("data_primeiro_pagamento", ""))
        if not data_primeiro_pag:
            return {"juros_parcelamento": 0, "valor_total_parcelado": saldo_base}
        
        frequencia = params.get("frequencia_pagamento", "Quinzenal")
        tipo_calculo = params.get("tipo_calculo_parcela", "por_valor")
        taxa_dia_decimal = self.get_float(params.get("taxa_encargos_dia", "0.40")) / 100.0
        
        if tipo_calculo == "por_valor":
            valor_parcela_desejada = self.get_float(params.get("valor_parcela_desejada", "100"))
            num_parcelas = math.ceil(saldo_base / valor_parcela_desejada) if valor_parcela_desejada > 0 else 1
        else:
            num_parcelas = self.get_int(params.get("numero_parcelas_desejado", "3"))
        
        num_parcelas = min(max(1, num_parcelas), self.MAX_PARCELAS_ITER)
        
        # Calcular juros do parcelamento baseado na data média
        datas_parcelas = self._gerar_datas_parcelas(data_primeiro_pag, num_parcelas, frequencia)
        data_media_idx = math.ceil(num_parcelas / 2.0) - 1
        data_media = datas_parcelas[min(data_media_idx, len(datas_parcelas) - 1)]
        
        dias_financiamento = (data_media - data_primeiro_pag).days
        juros_parcelamento = saldo_base * taxa_dia_decimal * dias_financiamento if dias_financiamento > 0 else 0
        
        valor_total_parcelado = saldo_base + juros_parcelamento
        valor_cada_parcela = valor_total_parcelado / num_parcelas
        
        parcelas_info = []
        for i, data_parcela in enumerate(datas_parcelas):
            parcelas_info.append({
                "numero": i + 1,
                "data": data_parcela.strftime("%d/%m/%Y"),
                "valor": valor_cada_parcela
            })
        
        return {
            "juros_parcelamento": juros_parcelamento,
            "valor_total_parcelado": valor_total_parcelado,
            "num_parcelas": num_parcelas,
            "valor_cada_parcela": valor_cada_parcela,
            "parcelas_info": parcelas_info
        }

    def _gerar_datas_parcelas(self, data_inicio, num_parcelas, frequencia):
        datas = []
        data_atual = data_inicio
        delta_days = 7 if frequencia == "Semanal" else 15
        
        for _ in range(num_parcelas):
            datas.append(data_atual)
            data_atual += timedelta(days=delta_days)
        
        return datas

    def gerar_texto_negociacao(self):
        if not self.current_negotiation_details:
            return {"success": False, "message": "Calcule uma negociação primeiro"}
        
        details = self.current_negotiation_details
        texto_final = []
        
        # Feedback inicial - mostrar todas as NFs e seus valores originais
        texto_final.append("RESUMO DAS NOTAS FISCAIS EM NEGOCIAÇÃO:")
        for nf in details.get("nfs", []):
            texto_final.append(f"NF: {nf['num_nf']} - Valor da Fatura: R$ {nf['valor_original']:.2f}")
        texto_final.append("")  # Linha em branco para separar
        texto_final.append("=" * 50)
        texto_final.append("")
        
        # Check if multa is applied based on the NFs data
        aplica_multa = any(nf.get('multa_calculada', 0) > 0 for nf in details.get("nfs", []))
        
        if details["tipo_pagamento"] == "avista":
            if len(details["nfs"]) == 1:
                nf = details["nfs"][0]
                texto_final.append("Pagamento à vista de apenas um título:")
                texto_final.append(f"NF: {nf['num_nf']}")
                texto_final.append(f"Valor Original: R$ {nf['valor_original']:.2f}")
                texto_final.append(f"Juros Mora: R$ {nf.get('juros_mora_calculado', 0.0):.2f}")
                if aplica_multa and nf.get('multa_calculada', 0.0) > 0:
                    texto_final.append(f"Multa: R$ {nf.get('multa_calculada', 0.0):.2f}")
                if float(details['desconto_juros_valor']) > 0:
                    texto_final.append(f"Desconto Juros Mora: R$ {details['desconto_juros_valor']:.2f}")
                texto_final.append(f"VALOR FINAL PARA PAGAMENTO À VISTA: R$ {float(details['saldo_devedor_base_apos_desconto']):.2f}")
            else:
                texto_final.append("Pagamento à vista de vários títulos:")
                for nf in details["nfs"]:
                    valor_nf_atualizado = nf.get('valor_atualizado_calculado', nf['valor_original'])
                    texto_final.append(f"NF: {nf['num_nf']} - Valor Atualizado (c/ encargos da NF): R$ {valor_nf_atualizado:.2f}")
                texto_final.append("---")
                texto_final.append(f"Total Principal Original: R$ {details['total_principal']:.2f}")
                texto_final.append(f"Total Juros Mora: R$ {details['total_juros_mora']:.2f}")
                if aplica_multa and float(details['total_multas']) > 0:
                    texto_final.append(f"Total Multas Aplicadas: R$ {details['total_multas']:.2f}")
                texto_final.append(f"Saldo Devedor Bruto: R$ {float(details['total_principal']) + float(details['total_juros_mora']) + float(details['total_multas']):.2f}")
                if float(details['desconto_juros_valor']) > 0:
                    texto_final.append(f"Desconto Total Juros Mora: R$ {details['desconto_juros_valor']:.2f}")
                texto_final.append(f"VALOR TOTAL PARA PAGAMENTO À VISTA: R$ {float(details['saldo_devedor_base_apos_desconto']):.2f}")
        
        elif details["tipo_pagamento"] == "parcelado":
            texto_final.append("Pagamento parcelado:")
            for nf in details["nfs"]:
                valor_nf_atualizado = nf.get('valor_atualizado_calculado', nf['valor_original'])
                texto_final.append(f"NF: {nf['num_nf']} - Valor Atualizado (c/ encargos da NF): R$ {valor_nf_atualizado:.2f}")
            texto_final.append("---")
            texto_final.append(f"Saldo Devedor Base (após descontos de mora): R$ {float(details['saldo_devedor_base_apos_desconto']):.2f}")
            texto_final.append(f"Juros do Parcelamento (Data Média): R$ {details.get('juros_financiamento_data_media', '0.00')}")
            texto_final.append(f"VALOR TOTAL A PARCELAR (COM JUROS DO PARCELAMENTO): R$ {details.get('valor_total_final_com_juros_parcelamento', '0.00')}")
            texto_final.append("---")
            
            if details.get("parcelas_info"):
                for i, p_info in enumerate(details["parcelas_info"]):
                    texto_final.append(f"{i+1}° Pagamento dia {p_info['data']} - R$ {p_info['valor']:.2f}")
            else:
                texto_final.append(f"{details.get('num_parcelas_final', 'N/A')} parcelas de R$ {details.get('valor_parcela_final', 'N/A')}")
            
            texto_final.append(f"Total Final Parcelado: R$ {details.get('total_final_parcelado', 'N/A')}")
        
        return {"success": True, "texto": "\n".join(texto_final)}


def main():
    api = CalculadoraAPI()
    
    window = webview.create_window(
        title="Calculadora de Negociação de Dívidas",
        url="index.html",
        js_api=api,
        width=1200,
        height=900,
        min_size=(800, 600),
        resizable=True
    )
    
    webview.start(debug=True)


if __name__ == "__main__":
    main()
