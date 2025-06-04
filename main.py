from openpyxl import load_workbook
from datetime import datetime
import requests
from config import TOKEN,CHAT_ID

# CONFIGURAÇÕES 
CAMINHO_PLANILHA = 'vendas_de_lanches.xlsx'



# COLETAR DADOS DO USUÁRIO 
print("📋 CADASTRO DE NOVO PEDIDO")

produto = input("Produto: ")
quantidade = int(input("Quantidade: "))
preco_unitario = float(input("Preço unitário (R$): ").replace(',', '.'))
forma_pagamento = input("Forma de pagamento: ")
nome_cliente = input("Nome do cliente: ")

data_hoje = datetime.today().strftime('%d/%m/%Y')
valor_total = quantidade * preco_unitario

# INSERIR NA PLANILHA 
try:
    planilha = load_workbook(CAMINHO_PLANILHA)
    aba = planilha.active

    aba.append([
        produto,
        quantidade,
        preco_unitario,
        valor_total,
        forma_pagamento
    ])

    planilha.save(CAMINHO_PLANILHA)
    print("✅ Pedido salvo na planilha.")
except Exception as e:
    print("❌ Erro ao salvar na planilha:", e)

# ENVIAR PARA O TELEGRAM 
mensagem = (
    f"📦 *Novo Pedido Registrado!*\n\n"
    f"👤 Cliente: {nome_cliente}\n"
    f"🛒 Produto: {produto}\n"
    f"🔢 Quantidade: {quantidade}\n"
    f"💰 Total: R$ {valor_total:.2f}\n"
    f"📅 Data: {data_hoje}\n"
    f"💳 Pagamento: {forma_pagamento}"
)

url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
dados = {
    'chat_id': CHAT_ID,
    'text': mensagem,
    'parse_mode': 'Markdown'
}

try:
    resposta = requests.post(url, data=dados)
    if resposta.status_code == 200:
        print("✅ Confirmação enviada no Telegram.")
    else:
        print("❌ Erro ao enviar no Telegram:", resposta.text)
except Exception as e:
    print("❌ Erro de conexão ao enviar mensagem:", e)
