from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)
from openpyxl import load_workbook
from config import TOKEN

# CONFIGURAÇÕES 
PLANILHA = 'vendas_de_lanches.xlsx'

# ESTADOS DA CONVERSA 
CLIENTE, PRODUTO, QUANTIDADE, PRECO, PAGAMENTO = range(5)

# TECLADO DE PAGAMENTO 
pagamento_teclado = ReplyKeyboardMarkup(
    [['Dinheiro', 'Cartão'], ['PIX']], one_time_keyboard=True, resize_keyboard=True
)

# FLUXO DE CONVERSA 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Qual seu nome?",
        reply_markup=ReplyKeyboardRemove()
    )
    return CLIENTE

async def cliente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome = update.message.text
    context.user_data['cliente'] = nome  # salvando o nome

    await update.message.reply_text(
        f"Olá, {nome}! Me diga qual produto você deseja:"
    )
    return PRODUTO

async def produto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['produto'] = update.message.text
    await update.message.reply_text("Qual a quantidade?")
    return QUANTIDADE

async def quantidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    if not texto.isdigit():
        await update.message.reply_text("Por favor, informe um número válido para a quantidade.")
        return QUANTIDADE
    context.user_data['quantidade'] = int(texto)
    await update.message.reply_text("Qual o preço unitário?")
    return PRECO

async def preco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.replace(',', '.')
    try:
        preco = float(texto)
    except ValueError:
        await update.message.reply_text("Por favor, informe um preço válido (ex: 3.50).")
        return PRECO
    context.user_data['preco_unitario'] = preco
    await update.message.reply_text("Qual a forma de pagamento?", reply_markup=pagamento_teclado)
    return PAGAMENTO

async def pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    forma_pagamento = update.message.text
    context.user_data['pagamento'] = forma_pagamento

    total = context.user_data['quantidade'] * context.user_data['preco_unitario']

    try:
        wb = load_workbook(PLANILHA)
        ws = wb.active
        ws.append([
            context.user_data['produto'],
            context.user_data['cliente'],
            context.user_data['quantidade'],
            context.user_data['preco_unitario'],
            total,
            forma_pagamento
        ])
        wb.save(PLANILHA)
    except Exception as e:
        await update.message.reply_text(f"Erro ao salvar na planilha: {e}")
        return ConversationHandler.END

    await update.message.reply_text(
        f"✅ Pedido registrado!\n"
        f"👤 Cliente: {context.user_data['cliente']}\n"
        f"🛒 Produto: {context.user_data['produto']}\n"
        f"🔢 Quantidade: {context.user_data['quantidade']}\n"
        f"💵 Preço unitário: R$ {context.user_data['preco_unitario']:.2f}\n"
        f"💰 Total: R$ {total:.2f}\n"
        f"💳 Pagamento: {forma_pagamento}",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Pedido cancelado.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CLIENTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cliente)],
            PRODUTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, produto)],
            QUANTIDADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, quantidade)],
            PRECO: [MessageHandler(filters.TEXT & ~filters.COMMAND, preco)],
            PAGAMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, pagamento)],
        },
        fallbacks=[CommandHandler('cancel', cancelar)],
    )

    app.add_handler(conv_handler)

    print("🤖 Bot rodando...")
    app.run_polling()

if __name__ == '__main__':
    main()
