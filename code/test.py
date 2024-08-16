from datetime import datetime, date 

dia_atual = datetime.now()
dia_vencimento = datetime.strptime('10/07/2024', '%d/%m/%Y')
print((dia_atual - dia_vencimento).days)

# print((datetime.now().date() - date.fromisoformat('05/02/2024'.replace('/','-')).day))

