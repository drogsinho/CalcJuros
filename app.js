// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Set default dates
    const today = new Date();
    const defaultDate = formatDateToBR(today);
    const futureDate = formatDateToBR(new Date(today.getTime() + (15 * 24 * 60 * 60 * 1000)));
    
    document.getElementById('vencimentoNF').value = defaultDate;
    document.getElementById('dataBaseEncargos').value = defaultDate;
    document.getElementById('dataPrimeiroPagamento').value = futureDate;
    
    // Initialize form states
    toggleParcelamento();
    toggleTipoCalculo();
}

function formatDateToBR(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear() % 100;
    return `${day}/${month}/${year}`;
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function showLoading(show = true) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }
}

function showNotification(message, type = 'info') {
    // Create a simple notification system
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-md shadow-lg z-50 max-w-sm transition-all transform translate-x-full`;
    
    const bgColor = type === 'error' ? 'bg-red-500' : type === 'success' ? 'bg-green-500' : 'bg-blue-500';
    notification.className += ` ${bgColor} text-white`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

async function adicionarNF() {
    const numNF = document.getElementById('numNF').value.trim();
    const valorNF = document.getElementById('valorNF').value;
    const vencimentoNF = document.getElementById('vencimentoNF').value.trim();
    
    if (!numNF || !valorNF || !vencimentoNF) {
        showNotification('Preencha todos os campos da NF', 'error');
        return;
    }
    
    try {
        showLoading();
        
        // Check if pywebview API is available
        if (typeof pywebview === 'undefined' || !pywebview.api) {
            throw new Error('API não disponível');
        }
        
        const result = await pywebview.api.adicionar_nf(numNF, valorNF, vencimentoNF);
        
        if (result.success) {
            document.getElementById('numNF').value = '';
            document.getElementById('valorNF').value = '';
            document.getElementById('numNF').focus();
            
            updateNFsTable(result.nfs);
            showNotification('NF adicionada com sucesso!', 'success');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao adicionar NF:', error);
        showNotification('Erro ao adicionar NF: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function removerNF(numNF) {
    try {
        showLoading();
        const result = await pywebview.api.remover_nf(numNF);
        
        if (result.success) {
            updateNFsTable(result.nfs);
            showNotification('NF removida com sucesso!', 'success');
        } else {
            showNotification('Erro ao remover NF', 'error');
        }
    } catch (error) {
        console.error('Erro ao remover NF:', error);
        showNotification('Erro ao remover NF', 'error');
    } finally {
        showLoading(false);
    }
}

function updateNFsTable(nfs) {
    const tbody = document.getElementById('nfsTableBody');
    tbody.innerHTML = '';
    
    nfs.forEach(nf => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 slide-in';
        row.innerHTML = `
            <td class="px-3 py-2 text-sm text-gray-900">${nf.num_nf}</td>
            <td class="px-3 py-2 text-sm text-gray-900">${formatCurrency(nf.valor_original)}</td>
            <td class="px-3 py-2 text-sm text-gray-900">${nf.venc_str}</td>
            <td class="px-3 py-2 text-sm text-gray-900">${nf.dias_atraso || 0}</td>
            <td class="px-3 py-2 text-sm text-gray-900">${formatCurrency(nf.juros_mora || 0)}</td>
            <td class="px-3 py-2 text-sm text-gray-900">${formatCurrency(nf.multa || 0)}</td>
            <td class="px-3 py-2 text-sm font-medium text-gray-900">${formatCurrency(nf.valor_atualizado || nf.valor_original)}</td>
            <td class="px-3 py-2 text-sm">
                <button onclick="removerNF('${nf.num_nf}')" class="text-red-600 hover:text-red-800 transition-colors">
                    Remover
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function toggleParcelamento() {
    const formaPagamento = document.getElementById('formaPagamento').value;
    const parcelamentoOptions = document.getElementById('parcelamentoOptions');
    
    if (formaPagamento === 'parcelado') {
        parcelamentoOptions.classList.remove('hidden');
        parcelamentoOptions.classList.add('fade-in');
    } else {
        parcelamentoOptions.classList.add('hidden');
    }
}

function toggleTipoCalculo() {
    const tipoCalculo = document.getElementById('tipoCalculoParcela').value;
    const valorParcelaDiv = document.getElementById('valorParcelaDiv');
    const numeroParcelasDiv = document.getElementById('numeroParcelasDiv');
    
    if (tipoCalculo === 'por_valor') {
        valorParcelaDiv.classList.remove('hidden');
        numeroParcelasDiv.classList.add('hidden');
    } else {
        valorParcelaDiv.classList.add('hidden');
        numeroParcelasDiv.classList.remove('hidden');
    }
}

async function calcularNegociacao() {
    const params = {
        data_base_encargos: document.getElementById('dataBaseEncargos').value,
        taxa_encargos_dia: document.getElementById('taxaEncargos').value,
        desconto_juros: document.getElementById('descontoJuros').value,
        aplicar_multa: document.getElementById('aplicarMulta').checked,
        forma_pagamento: document.getElementById('formaPagamento').value,
        data_primeiro_pagamento: document.getElementById('dataPrimeiroPagamento').value,
        frequencia_pagamento: document.getElementById('frequenciaPagamento').value,
        tipo_calculo_parcela: document.getElementById('tipoCalculoParcela').value,
        valor_parcela_desejada: document.getElementById('valorParcela').value,
        numero_parcelas_desejado: document.getElementById('numeroParcelas').value
    };
    
    try {
        showLoading();
        const result = await pywebview.api.calcular_negociacao(params);
        
        if (result.success) {
            updateResultados(result);
            showNotification('Negociação calculada com sucesso!', 'success');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao calcular negociação:', error);
        showNotification('Erro ao calcular negociação', 'error');
    } finally {
        showLoading(false);
    }
}

function updateResultados(result) {
    // Update basic results
    document.getElementById('totalPrincipal').textContent = formatCurrency(result.total_principal);
    document.getElementById('totalJuros').textContent = formatCurrency(result.total_juros);
    document.getElementById('totalMultas').textContent = formatCurrency(result.total_multas);
    document.getElementById('saldoBase').textContent = formatCurrency(result.saldo_base);
    
    // Update NFs table with calculated values
    updateNFsTable(result.nfs_calculadas);
    
    // Handle parcelamento results
    const resultadosParcelamento = document.getElementById('resultadosParcelamento');
    const parcelasDetalhes = document.getElementById('parcelasDetalhes');
    
    if (result.parcelas_info && result.parcelas_info.length > 0) {
        resultadosParcelamento.classList.remove('hidden');
        parcelasDetalhes.classList.remove('hidden');
        
        document.getElementById('jurosParcelamento').textContent = formatCurrency(result.juros_parcelamento || 0);
        document.getElementById('numParcelasResult').textContent = result.num_parcelas || 0;
        document.getElementById('valorParcelaResult').textContent = formatCurrency(result.valor_cada_parcela || 0);
        document.getElementById('totalParcelado').textContent = formatCurrency(result.valor_total_parcelado || 0);
        
        // Update parcelas details
        const parcelasLista = document.getElementById('parcelasLista');
        parcelasLista.innerHTML = '';
        
        result.parcelas_info.forEach(parcela => {
            const div = document.createElement('div');
            div.className = 'flex justify-between text-gray-600';
            div.innerHTML = `
                <span>${parcela.numero}ª: ${parcela.data}</span>
                <span>${formatCurrency(parcela.valor)}</span>
            `;
            parcelasLista.appendChild(div);
        });
    } else {
        resultadosParcelamento.classList.add('hidden');
        parcelasDetalhes.classList.add('hidden');
    }
}

async function gerarTexto() {
    try {
        showLoading();
        const result = await pywebview.api.gerar_texto_negociacao();
        
        if (result.success) {
            document.getElementById('textoNegociacao').textContent = result.texto;
            document.getElementById('textModal').classList.remove('hidden');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao gerar texto:', error);
        showNotification('Erro ao gerar texto', 'error');
    } finally {
        showLoading(false);
    }
}

function copiarTexto() {
    const texto = document.getElementById('textoNegociacao').textContent;
    navigator.clipboard.writeText(texto).then(() => {
        showNotification('Texto copiado para a área de transferência!', 'success');
    }).catch(() => {
        showNotification('Erro ao copiar texto', 'error');
    });
}

function fecharModal() {
    document.getElementById('textModal').classList.add('hidden');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target.closest('#numNF, #valorNF, #vencimentoNF')) {
        adicionarNF();
    }
    
    if (e.key === 'Escape') {
        fecharModal();
    }
    
    if (e.ctrlKey && e.key === 'Enter') {
        calcularNegociacao();
    }
});
