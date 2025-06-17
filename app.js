// inicializar o aplicativo
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeDarkMode();
});

function initializeApp() {
    // definir datas padrão
    const today = new Date();
    const defaultDate = formatDateToBR(today);
    const futureDate = formatDateToBR(new Date(today.getTime() + (15 * 24 * 60 * 60 * 1000)));
    
    document.getElementById('vencimentoNF').value = defaultDate;
    document.getElementById('dataBaseEncargos').value = defaultDate;
    document.getElementById('dataPrimeiroPagamento').value = defaultDate;
    
    // inicializar estados do formulário
    toggleParcelamento();
    toggleTipoCalculo();
}

function initializeDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const sunIcon = document.getElementById('sunIcon');
    const moonIcon = document.getElementById('moonIcon');
    
    // verificar preferência de tema salvo ou padrão para tema claro
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.classList.add('dark');
        sunIcon.classList.add('hidden');
        moonIcon.classList.remove('hidden');
    }
    
    darkModeToggle.addEventListener('click', toggleDarkMode);
}

function toggleDarkMode() {
    const html = document.documentElement;
    const sunIcon = document.getElementById('sunIcon');
    const moonIcon = document.getElementById('moonIcon');
    
    html.classList.toggle('dark');
    
    if (html.classList.contains('dark')) {
        localStorage.setItem('theme', 'dark');
        sunIcon.classList.add('hidden');
        moonIcon.classList.remove('hidden');
    } else {
        localStorage.setItem('theme', 'light');
        sunIcon.classList.remove('hidden');
        moonIcon.classList.add('hidden');
    }
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
    // criar um sistema de notificacao simples
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-md shadow-lg z-50 max-w-sm transition-all transform translate-x-full`;
    
    const bgColor = type === 'error' ? 'bg-red-500' : type === 'success' ? 'bg-green-500' : 'bg-blue-500';
    notification.className += ` ${bgColor} text-white`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // animação in	
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // remove dps de 3 segundos
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
        
        // verificar se a API do pywebview está disponível
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

async function removerTodasNFs() {
    const nfsTableBody = document.getElementById('nfsTableBody');

    // verificar se há alguma NF atualmente na tabela
    if (nfsTableBody.children.length === 0) {
        showNotification('Nenhuma NF para remover.', 'info');
        return; // sair se não houver NFs para remover
    }

    try {
        showLoading();
        const result = await pywebview.api.remover_todas_nfs();

        if (result.success) {
            updateNFsTable(result.nfs); // nfs deve ser uma lista vazia
            showNotification('Todas as NFs foram removidas com sucesso!', 'success');
        } else {
            showNotification('Erro ao remover todas as NFs', 'error');
        }
    } catch (error) {
        console.error('Erro ao remover todas as NFs:', error);
        showNotification('Erro ao remover todas as NFs', 'error');
    } finally {
        // este bloco 'finally' só será alcançado se a função não tiver retornado antes
        // (ou seja, se houver NFs para tentar remover e showLoading() tiver sido chamado).
        showLoading(false);
    }
}

function updateNFsTable(nfs) {
    const tbody = document.getElementById('nfsTableBody');
    tbody.innerHTML = '';
    
    nfs.forEach(nf => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 dark:hover:bg-gray-700 slide-in';
        row.innerHTML = `
            <td class="px-3 py-2 text-sm text-gray-900 dark:text-gray-100">${nf.num_nf}</td>
            <td class="px-3 py-2 text-sm text-gray-900 dark:text-gray-100">${formatCurrency(nf.valor_original)}</td>
            <td class="px-3 py-2 text-sm text-gray-900 dark:text-gray-100">${nf.venc_str}</td>
            <td class="px-3 py-2 text-sm text-gray-900 dark:text-gray-100">${nf.dias_atraso || 0}</td>
            <td class="px-3 py-2 text-sm text-gray-900 dark:text-gray-100">${formatCurrency(nf.juros_mora || 0)}</td>
            <td class="px-3 py-2 text-sm text-gray-900 dark:text-gray-100">${formatCurrency(nf.multa || 0)}</td>
            <td class="px-3 py-2 text-sm font-medium text-gray-900 dark:text-gray-100">${formatCurrency(nf.valor_atualizado || nf.valor_original)}</td>
            <td class="px-3 py-2 text-sm">
                <button onclick="removerNF('${nf.num_nf}')" class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 transition-colors">
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
    try {
        showLoading(true);
        
        const params = {
            data_base_encargos: document.getElementById('dataBaseEncargos').value,
            taxa_encargos_dia: document.getElementById('taxaEncargos').value,
            aplicar_multa: document.getElementById('aplicarMulta').checked,
            desconto_juros: document.getElementById('descontoJuros').value,
            forma_pagamento: document.getElementById('formaPagamento').value
        };

        if (params.forma_pagamento === 'parcelado') {
            params.data_primeiro_pagamento = document.getElementById('dataPrimeiroPagamento').value;
            params.frequencia_pagamento = document.getElementById('frequenciaPagamento').value;
            params.tipo_calculo_parcela = document.getElementById('tipoCalculoParcela').value;
            
            if (params.tipo_calculo_parcela === 'por_valor') {
                params.valor_parcela_desejada = document.getElementById('valorParcela').value;
            } else {
                params.numero_parcelas_desejado = document.getElementById('numeroParcelas').value;
            }
        }

        const result = await window.pywebview.api.calcular_negociacao(params);
        
        if (result.success) {
            updateResultados(result);
            document.getElementById('btnSalvarAtual').classList.remove('hidden');
            showNotification('Cálculo realizado com sucesso!', 'success');
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
    // atualizar resultados basicos
    document.getElementById('totalPrincipal').textContent = formatCurrency(result.total_principal);
    document.getElementById('totalJuros').textContent = formatCurrency(result.total_juros);
    document.getElementById('totalMultas').textContent = formatCurrency(result.total_multas);
    document.getElementById('saldoBase').textContent = formatCurrency(result.saldo_base);
    
    // atualizar tabela NFs com valores calculados
    updateNFsTable(result.nfs_calculadas);
    
    // lidar com resultados de parcelamento
    const resultadosParcelamento = document.getElementById('resultadosParcelamento');
    const parcelasDetalhes = document.getElementById('parcelasDetalhes');
    
    if (result.parcelas_info && result.parcelas_info.length > 0) {
        resultadosParcelamento.classList.remove('hidden');
        parcelasDetalhes.classList.remove('hidden');
        
        document.getElementById('jurosParcelamento').textContent = formatCurrency(result.juros_parcelamento || 0);
        document.getElementById('numParcelasResult').textContent = result.num_parcelas || 0;
        document.getElementById('valorParcelaResult').textContent = formatCurrency(result.valor_cada_parcela || 0);
        document.getElementById('totalParcelado').textContent = formatCurrency(result.valor_total_parcelado || 0);
        
        // atualizar detalhes das parcelas
        const parcelasLista = document.getElementById('parcelasLista');
        parcelasLista.innerHTML = '';
        
        result.parcelas_info.forEach(parcela => {
            const div = document.createElement('div');
            div.className = 'flex justify-between text-gray-600 dark:text-gray-400';
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

// atalhos de teclado
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

// Funções para gerenciar as abas
function showTab(tabName) {
    const calculadoraTab = document.getElementById('tabCalculadora');
    const negociacoesTab = document.getElementById('tabNegociacoes');
    const conteudoCalculadora = document.getElementById('conteudoCalculadora');
    const conteudoNegociacoes = document.getElementById('conteudoNegociacoes');
    
    if (tabName === 'calculadora') {
        calculadoraTab.classList.add('text-primary-600', 'dark:text-primary-400', 'border-b-2', 'border-primary-600', 'dark:border-primary-400');
        calculadoraTab.classList.remove('text-gray-500', 'dark:text-gray-400');
        negociacoesTab.classList.remove('text-primary-600', 'dark:text-primary-400', 'border-b-2', 'border-primary-600', 'dark:border-primary-400');
        negociacoesTab.classList.add('text-gray-500', 'dark:text-gray-400');
        conteudoCalculadora.classList.remove('hidden');
        conteudoNegociacoes.classList.add('hidden');
    } else {
        negociacoesTab.classList.add('text-primary-600', 'dark:text-primary-400', 'border-b-2', 'border-primary-600', 'dark:border-primary-400');
        negociacoesTab.classList.remove('text-gray-500', 'dark:text-gray-400');
        calculadoraTab.classList.remove('text-primary-600', 'dark:text-primary-400', 'border-b-2', 'border-primary-600', 'dark:border-primary-400');
        calculadoraTab.classList.add('text-gray-500', 'dark:text-gray-400');
        conteudoNegociacoes.classList.remove('hidden');
        conteudoCalculadora.classList.add('hidden');
        carregarNegociacoes();
    }
}

// Funções para gerenciar negociações
async function salvarNegociacao() {
    const numeroCliente = document.getElementById('numeroCliente').value.trim();
    const nomeCliente = document.getElementById('nomeCliente').value.trim();
    const observacoes = document.getElementById('observacoesNegociacao').value.trim();
    
    if (!numeroCliente || !nomeCliente) {
        showNotification('Preencha o número e nome do cliente', 'error');
        return;
    }
    
    try {
        showLoading();
        const result = await pywebview.api.salvar_negociacao({
            numero_cliente: numeroCliente,
            nome_cliente: nomeCliente,
            observacoes: observacoes,
            data_negociacao: new Date().toISOString(),
            status: 'Pendente'
        });
        
        if (result.success) {
            limparFormularioNegociacao();
            carregarNegociacoes();
            showNotification('Negociação salva com sucesso!', 'success');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar negociação:', error);
        showNotification('Erro ao salvar negociação', 'error');
    } finally {
        showLoading(false);
    }
}

async function salvarNegociacaoAtual() {
    const numeroCliente = document.getElementById('numeroCliente').value.trim();
    const nomeCliente = document.getElementById('nomeCliente').value.trim();
    const observacoes = document.getElementById('observacoesNegociacao').value.trim();
    
    if (!numeroCliente || !nomeCliente) {
        showNotification('Preencha o número e nome do cliente', 'error');
        return;
    }
    
    try {
        showLoading();
        const result = await pywebview.api.salvar_negociacao_atual({
            numero_cliente: numeroCliente,
            nome_cliente: nomeCliente,
            observacoes: observacoes,
            data_negociacao: new Date().toISOString(),
            status: 'Pendente'
        });
        
        if (result.success) {
            limparFormularioNegociacao();
            carregarNegociacoes();
            showNotification('Negociação atual salva com sucesso!', 'success');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar negociação atual:', error);
        showNotification('Erro ao salvar negociação atual', 'error');
    } finally {
        showLoading(false);
    }
}

function limparFormularioNegociacao() {
    document.getElementById('numeroCliente').value = '';
    document.getElementById('nomeCliente').value = '';
    document.getElementById('observacoesNegociacao').value = '';
}

async function carregarNegociacoes() {
    try {
        showLoading();
        const result = await pywebview.api.listar_negociacoes();
        
        if (result.success) {
            atualizarTabelaNegociacoes(result.negociacoes);
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao carregar negociações:', error);
        showNotification('Erro ao carregar negociações', 'error');
    } finally {
        showLoading(false);
    }
}

// Função para obter a classe de cor do status
function getStatusColorClass(status) {
    return status === 'Pago' ? 'bg-green-100 text-green-800 border-green-300' :
           status === 'Pendente' ? 'bg-red-100 text-red-800 border-red-300' :
           'bg-yellow-100 text-yellow-800 border-yellow-300';
}

// Função para atualizar a tabela de negociações
function atualizarTabelaNegociacoes(negociacoes) {
    const tbody = document.getElementById('negociacoesTableBody');
    tbody.innerHTML = '';

    negociacoes.forEach(negociacao => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50 dark:hover:bg-gray-700';
        
        const statusClass = getStatusColorClass(negociacao.status);
        
        tr.innerHTML = `
            <td class="px-3 py-2 text-sm text-gray-900 dark:text-white">${negociacao.numero_cliente} - ${negociacao.nome_cliente}</td>
            <td class="px-3 py-2 text-sm text-gray-900 dark:text-white">${new Date(negociacao.data_negociacao).toLocaleDateString('pt-BR')}</td>
            <td class="px-3 py-2 text-sm text-gray-900 dark:text-white">${formatCurrency(negociacao.valor_total)}</td>
            <td class="px-3 py-2 text-sm">
                <span class="px-2 py-1 rounded-full text-xs font-medium ${statusClass}">
                    ${negociacao.status}
                </span>
            </td>
            <td class="px-3 py-2 text-sm text-gray-900 dark:text-white">
                <div class="flex space-x-2">
                    <button onclick="visualizarNegociacao('${negociacao.id}')" class="text-primary-600 hover:text-primary-700">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                        </svg>
                    </button>
                    <button onclick="editarNegociacao('${negociacao.id}')" class="text-yellow-600 hover:text-yellow-700">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                    </button>
                    <button onclick="excluirNegociacao('${negociacao.id}')" class="text-red-600 hover:text-red-700">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function visualizarNegociacao(id) {
    try {
        showLoading();
        const result = await pywebview.api.obter_negociacao(id);
        
        if (result.success) {
            const negociacao = result.negociacao;
            
            // Armazenar o ID da negociação no modal
            document.getElementById('viewNegociacaoModal').setAttribute('data-id', negociacao.id);
            
            // Preencher informações básicas
            document.getElementById('viewCliente').textContent = `${negociacao.numero_cliente} - ${negociacao.nome_cliente}`;
            document.getElementById('viewData').textContent = new Date(negociacao.data_negociacao).toLocaleDateString('pt-BR');
            document.getElementById('viewValorTotal').textContent = formatCurrency(negociacao.valor_total);
            
            // Atualizar status com cores
            const statusSelect = document.getElementById('viewStatusSelect');
            statusSelect.value = negociacao.status;
            statusSelect.className = `border rounded-md px-3 py-1 text-sm ${getStatusColorClass(negociacao.status)}`;

            // Observações editáveis
            const observacoesDiv = document.getElementById('viewObservacoes');
            observacoesDiv.innerHTML = `
                <div class="flex flex-col space-y-2">
                    <div class="flex justify-between items-start">
                        <p class="text-gray-900 dark:text-white whitespace-pre-wrap">${negociacao.observacoes || 'Sem observações'}</p>
                        <div class="flex space-x-2">
                            <button onclick="editarObservacoes()" class="text-primary-600 hover:text-primary-700">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">
                        <span class="cursor-pointer hover:text-primary-600" onclick="copiarTextoSelecionado(this)">Clique para selecionar e copiar texto</span>
                    </div>
                </div>
            `;

            // Preencher NFs
            const nfsContainer = document.getElementById('viewNfs');
            nfsContainer.innerHTML = '';
            if (negociacao.detalhes && negociacao.detalhes.nfs_calculadas) {
                const nfsHeader = document.createElement('div');
                nfsHeader.className = 'mb-4';
                nfsHeader.innerHTML = '<h4 class="font-medium text-gray-900 dark:text-white mb-2">Notas Fiscais:</h4>';
                nfsContainer.appendChild(nfsHeader);

                negociacao.detalhes.nfs_calculadas.forEach(nf => {
                    const nfDiv = document.createElement('div');
                    nfDiv.className = 'bg-gray-50 dark:bg-gray-700 p-3 rounded mb-2';
                    nfDiv.innerHTML = `
                        <div class="flex justify-between items-center">
                            <div>
                                <span class="font-medium">NF: ${nf.num_nf}</span>
                                <div class="text-sm text-gray-600 dark:text-gray-400">
                                    Vencimento: ${nf.venc_str} | Dias Atraso: ${nf.dias_atraso}
                                </div>
                            </div>
                            <div class="text-right">
                                <div class="text-sm text-gray-600 dark:text-gray-400">Valor Original: ${formatCurrency(nf.valor_original)}</div>
                                <div class="text-sm text-gray-600 dark:text-gray-400">Juros: ${formatCurrency(nf.juros_mora)}</div>
                                ${nf.multa > 0 ? `<div class="text-sm text-gray-600 dark:text-gray-400">Multa: ${formatCurrency(nf.multa)}</div>` : ''}
                                <div class="font-medium text-gray-900 dark:text-white">Total: ${formatCurrency(nf.valor_atualizado)}</div>
                            </div>
                        </div>
                    `;
                    nfsContainer.appendChild(nfDiv);
                });
            }

            // Preencher detalhes do parcelamento se existir
            const parcelasContainer = document.getElementById('viewParcelas');
            const parcelasList = document.getElementById('viewParcelasList');
            parcelasList.innerHTML = '';
            
            if (negociacao.detalhes && negociacao.detalhes.parcelas_info && negociacao.detalhes.parcelas_info.length > 0) {
                parcelasContainer.classList.remove('hidden');
                
                // Adicionar informações do parcelamento
                const parcelamentoInfo = document.createElement('div');
                parcelamentoInfo.className = 'mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded';
                parcelamentoInfo.innerHTML = `
                    <h4 class="font-medium text-gray-900 dark:text-white mb-3">Detalhes do Parcelamento</h4>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <p class="text-sm text-gray-600 dark:text-gray-400">Frequência:</p>
                            <p class="font-medium text-gray-900 dark:text-white">${negociacao.detalhes.frequencia_pagamento || 'Não definida'}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600 dark:text-gray-400">Tipo de Cálculo:</p>
                            <p class="font-medium text-gray-900 dark:text-white">${negociacao.detalhes.tipo_calculo_parcela === 'por_valor' ? 'Valor da Parcela' : 'Número de Parcelas'}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600 dark:text-gray-400">Quantidade de Parcelas:</p>
                            <p class="font-medium text-gray-900 dark:text-white">${negociacao.detalhes.num_parcelas || negociacao.detalhes.parcelas_info.length}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600 dark:text-gray-400">Valor da Parcela:</p>
                            <p class="font-medium text-gray-900 dark:text-white">${formatCurrency(negociacao.detalhes.valor_cada_parcela || 0)}</p>
                        </div>
                    </div>
                `;
                parcelasList.appendChild(parcelamentoInfo);

                // Adicionar lista de parcelas
                const parcelasHeader = document.createElement('div');
                parcelasHeader.className = 'mb-3';
                parcelasHeader.innerHTML = '<h4 class="font-medium text-gray-900 dark:text-white">Parcelas:</h4>';
                parcelasList.appendChild(parcelasHeader);

                let temAtraso = false;
                negociacao.detalhes.parcelas_info.forEach(parcela => {
                    const dataVencimento = new Date(parcela.data.split('/').reverse().join('-'));
                    const hoje = new Date();
                    const emAtraso = dataVencimento < hoje && !parcela.pago;
                    if (emAtraso) temAtraso = true;
                    
                    const parcelaDiv = document.createElement('div');
                    parcelaDiv.className = `bg-gray-50 dark:bg-gray-700 p-3 rounded mb-2 flex justify-between items-center ${emAtraso ? 'border-l-4 border-red-500' : ''}`;
                    parcelaDiv.innerHTML = `
                        <div>
                            <span class="font-medium">${parcela.numero}ª Parcela</span>
                            <div class="text-sm text-gray-600 dark:text-gray-400">
                                Vencimento: ${parcela.data}
                                ${emAtraso ? '<span class="text-red-500 ml-2">(Em Atraso)</span>' : ''}
                            </div>
                        </div>
                        <div class="flex items-center space-x-4">
                            <span class="font-medium">${formatCurrency(parcela.valor)}</span>
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" 
                                       class="sr-only peer" 
                                       ${parcela.pago ? 'checked' : ''}
                                       onchange="marcarParcelaPaga('${negociacao.id}', ${parcela.numero}, this.checked)">
                                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                                <span class="ml-3 text-sm text-gray-600 dark:text-gray-400">Pago</span>
                            </label>
                        </div>
                    `;
                    parcelasList.appendChild(parcelaDiv);
                });

                // Atualizar status se houver atraso
                if (temAtraso && negociacao.status !== 'Pago') {
                    statusSelect.value = 'Pendente';
                    statusSelect.className = 'border rounded-md px-3 py-1 text-sm bg-red-100 text-red-800 border-red-300';
                    await pywebview.api.atualizar_status_negociacao(negociacao.id, 'Pendente');
                }
            } else {
                parcelasContainer.classList.add('hidden');
            }

            // Mostrar modal
            document.getElementById('viewNegociacaoModal').classList.remove('hidden');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao visualizar negociação:', error);
        showNotification('Erro ao visualizar negociação', 'error');
    } finally {
        showLoading(false);
    }
}

// Função para copiar texto selecionado
function copiarTextoSelecionado(element) {
    const selection = window.getSelection();
    if (selection.toString().length > 0) {
        navigator.clipboard.writeText(selection.toString()).then(() => {
            showNotification('Texto copiado com sucesso!', 'success');
        }).catch(() => {
            showNotification('Erro ao copiar texto', 'error');
        });
    } else {
        showNotification('Selecione um texto para copiar', 'info');
    }
}

// Função para editar observações
async function editarObservacoes() {
    const observacoesAtuais = document.getElementById('viewObservacoes').textContent;
    const novaObservacao = prompt('Editar observações:', observacoesAtuais);
    
    if (novaObservacao !== null) {
        try {
            const id = document.getElementById('viewNegociacaoModal').getAttribute('data-id');
            const result = await pywebview.api.atualizar_negociacao(id, {
                observacoes: novaObservacao
            });
            
            if (result.success) {
                document.getElementById('viewObservacoes').textContent = novaObservacao;
                showNotification('Observações atualizadas com sucesso!', 'success');
            } else {
                showNotification(result.message, 'error');
            }
        } catch (error) {
            console.error('Erro ao atualizar observações:', error);
            showNotification('Erro ao atualizar observações', 'error');
        }
    }
}

async function excluirNegociacao(id) {
    if (!confirm('Tem certeza que deseja excluir esta negociação?')) {
        return;
    }
    
    try {
        showLoading();
        const result = await pywebview.api.excluir_negociacao(id);
        
        if (result.success) {
            carregarNegociacoes();
            showNotification('Negociação excluída com sucesso!', 'success');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao excluir negociação:', error);
        showNotification('Erro ao excluir negociação', 'error');
    } finally {
        showLoading(false);
    }
}

async function buscarNegociacao() {
    const searchTerm = document.getElementById('searchNegociacao').value.trim();
    if (!searchTerm) {
        carregarNegociacoes();
        return;
    }

    try {
        showLoading();
        const result = await pywebview.api.buscar_negociacao(searchTerm);
        
        if (result.success) {
            atualizarTabelaNegociacoes(result.negociacoes);
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao buscar negociação:', error);
        showNotification('Erro ao buscar negociação', 'error');
    } finally {
        showLoading(false);
    }
}

async function atualizarStatusNegociacao() {
    const id = document.getElementById('viewNegociacaoModal').getAttribute('data-id');
    const novoStatus = document.getElementById('viewStatusSelect').value;
    
    try {
        const result = await pywebview.api.atualizar_status_negociacao(id, novoStatus);
        
        if (result.success) {
            showNotification('Status atualizado com sucesso!', 'success');
            // Atualizar a cor do status no select
            document.getElementById('viewStatusSelect').className = `border rounded-md px-3 py-1 text-sm ${getStatusColorClass(novoStatus)}`;
            // Recarregar a lista de negociações para atualizar as cores
            await carregarNegociacoes();
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao atualizar status:', error);
        showNotification('Erro ao atualizar status', 'error');
    }
}

async function marcarParcelaPaga(negociacaoId, numeroParcela, pago) {
    try {
        showLoading();
        const result = await pywebview.api.marcar_parcela_paga(negociacaoId, numeroParcela, pago);
        
        if (result.success) {
            // Verificar se todas as parcelas foram pagas
            const resultVerificacao = await pywebview.api.verificar_status_parcelas(negociacaoId);
            if (resultVerificacao.success && resultVerificacao.todas_pagas) {
                // Atualizar status para "Pago" se todas as parcelas estiverem pagas
                await pywebview.api.atualizar_status_negociacao(negociacaoId, "Pago");
                document.getElementById('viewStatusSelect').value = "Pago";
            }
            showNotification('Status da parcela atualizado com sucesso!', 'success');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao atualizar status da parcela:', error);
        showNotification('Erro ao atualizar status da parcela', 'error');
    } finally {
        showLoading(false);
    }
}

function fecharModalNegociacao() {
    document.getElementById('viewNegociacaoModal').classList.add('hidden');
}

function fecharModalEdicaoNegociacao() {
    document.getElementById('editNegociacaoModal').classList.add('hidden');
}

async function editarNegociacao(id) {
    try {
        showLoading();
        const result = await pywebview.api.obter_negociacao(id);
        
        if (result.success) {
            const negociacao = result.negociacao;
            
            // Preencher formulário
            document.getElementById('editNegociacaoId').value = negociacao.id;
            document.getElementById('editNumeroCliente').value = negociacao.numero_cliente;
            document.getElementById('editNomeCliente').value = negociacao.nome_cliente;
            document.getElementById('editObservacoes').value = negociacao.observacoes || '';
            document.getElementById('editStatus').value = negociacao.status;
            
            // Mostrar modal
            document.getElementById('editNegociacaoModal').classList.remove('hidden');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao carregar negociação para edição:', error);
        showNotification('Erro ao carregar negociação para edição', 'error');
    } finally {
        showLoading(false);
    }
}

async function salvarEdicaoNegociacao() {
    const id = document.getElementById('editNegociacaoId').value;
    const params = {
        numero_cliente: document.getElementById('editNumeroCliente').value.trim(),
        nome_cliente: document.getElementById('editNomeCliente').value.trim(),
        observacoes: document.getElementById('editObservacoes').value.trim(),
        status: document.getElementById('editStatus').value
    };
    
    if (!params.numero_cliente || !params.nome_cliente) {
        showNotification('Preencha o número e nome do cliente', 'error');
        return;
    }
    
    try {
        showLoading();
        const result = await pywebview.api.atualizar_negociacao(id, params);
        
        if (result.success) {
            fecharModalEdicaoNegociacao();
            carregarNegociacoes();
            showNotification('Negociação atualizada com sucesso!', 'success');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao atualizar negociação:', error);
        showNotification('Erro ao atualizar negociação', 'error');
    } finally {
        showLoading(false);
    }
}
