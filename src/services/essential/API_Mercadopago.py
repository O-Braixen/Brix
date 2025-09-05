import pytz , mercadopago , os , uuid
from datetime import datetime, timedelta
from src.services.connection.database import BancoPagamentos
from dotenv import load_dotenv


# ======================================================================
load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) #load .env da raiz
mercadopagotoken = os.getenv("token_mercadopago")
sdk = mercadopago.SDK(mercadopagotoken)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))














# ======================================================================
# PARTE DE CRIAR E VERIFICAR SE EXISTE UM PAGAMENTO EXISTENTE
def criar_link_pagamento(user_id , quant_meses , preco , texto):
    # checa pagamento pendente antes de criar
    existente = BancoPagamentos.get_pending_payment(user_id, validade_hours=24)
    if existente:
        # devolve o qr/ticket do registro existente
        return (
            True,
            True,
            existente.get("mp_payment_id"),                # caso você tenha salvo com essa key
            existente.get("qr_code_base64"),
            existente.get("ticket_url"),
            existente.get("plano"),                               # documento salvo
            existente.get("created_at") + timedelta(hours=1)  # expiration_date estimada
        )
    
    # Data e hora atual em UTC com 1 hora de expiração
    now = datetime.now(pytz.utc)
    expiration_date = now + timedelta(hours=1)
    # Gera no formato exato exigido pela API
    date_str = expiration_date.strftime("%Y-%m-%dT%H:%M:%S.000%z")
    # Adiciona o ":" no offset de timezone
    date_str = date_str[:-2] + ":" + date_str[-2:]

    # PARTE DA PREFERENCIA DE PEDIDO, COM TODAS AS INFORMAÇÕES
    preference_data = { 
        "payment_method_id": "pix",
        "transaction_amount": float(preco*quant_meses),
        "description": f"Brix Premium ({texto})",
        "external_reference": f"{user_id}-{quant_meses}", 
        "notification_url": "https://brixbot.xyz/comprapremium",
        "payer": {
            "email": "comprador@email.com",
            "first_name": str(user_id),
            "last_name": str(user_id)
            },
        "date_of_expiration": date_str,
        "additional_info": {
            "items": [{
            "id": "1",
            "title": f"Brix Premium ({texto})",
            "description": "Assinatura Brix Premium.",
            "picture_url": "https://cdn.discordapp.com/emojis/1318962131567378432",
            "quantity": 1,
            "unit_price": float(preco*quant_meses)
        }]
        }
    }
    request_options = mercadopago.config.RequestOptions()
    request_options.custom_headers = {
        'x-idempotency-key': str(uuid.uuid4())
    }

    preference_response = sdk.payment().create(preference_data , request_options)
    resp = preference_response.get("response", {})

    # campos que a sua função insert espera
    mp_payment_id = resp.get("id")
    mp_status = resp.get("status")
    tx_data = resp.get("point_of_interaction", {}).get("transaction_data", {})
    qr_code_base64 = tx_data.get("qr_code_base64")
    ticket_url = tx_data.get("ticket_url")
    plano = f"Brix Premium ({texto})"  
    quant_meses = quant_meses

     # VERIFICA SE A API RETORNOU OS DADOS NECESSÁRIOS
    if not mp_payment_id or not qr_code_base64 or not ticket_url:
        print("Erro: Falha ao obter dados do QR Code.")
        return False , False, None, None, None, None, None
    
    # tenta inserir no banco
    try:
        BancoPagamentos.insert_payment( mp_payment_id=mp_payment_id, mp_status=mp_status, qr_code_base64=qr_code_base64, ticket_url=ticket_url, plano=plano, user_id=user_id , quant_meses=quant_meses )
    except Exception as e:
        # log mínimo e devolve erro
        print("Erro ao inserir pagamento:", e)
        # ainda devolve os dados do MP pra front, se quiser
        return False , False, mp_payment_id, qr_code_base64, ticket_url, plano, expiration_date

    return True , False, mp_payment_id, qr_code_base64, ticket_url, plano, expiration_date

















# ======================================================================
# PARTE PARA ATUALIZAR O STATUS DOS PAGAMENTOS, ESSA FUNÇÃO É CHAMADA SÓ PARA ATUALIZAR O PAGAMENTO
async def update_pagamentos(self):
    filtro = {"mp_status": {"$in": ["pending", "in_process", "pending_waiting_transfer"]},}
    busca = BancoPagamentos.select_by_filter(filtro)

    for pagamento in busca:
        
        try:
            request = sdk.payment().get(pagamento["mp_payment_id"])
            request = request.get("response", {})
            if pagamento["mp_status"] != request['status']:
                user = self.client.get_user(pagamento["user_id"])
                try:
                    dm_channel = await self.client.create_dm(user)
                    msg = await dm_channel.fetch_message(pagamento["msg_dm"])
                    await msg.delete()
                except:
                    print("falha ao deletar mensagem da DM")
                data = { "mp_status" : request['status']}
                BancoPagamentos.update_payment(pagamento["mp_payment_id"] , data )
                print(f"Pagamento {pagamento['mp_payment_id']} atualizado para {request['status']}")
            
            if request['status'] == "cancelled":
                BancoPagamentos.delete_by_mp_id(pagamento["mp_payment_id"])
                print(f"Registro {pagamento['mp_payment_id']} foi deletado do banco de dados")
                 

        except Exception as e:
            print("Erro ao consultar MP:", e)
            continue