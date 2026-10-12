"""Datos sintéticos de canastas para la sesión de venta cruzada (Semana 3+).
Reutiliza los 2,000 clientes de la base de Starbucks Rewards (data/customers.csv).
Estructura plantada:
  - 6 grupos de gusto (para filtrado colaborativo)
  - 6 pares bebida->comida con asociación fuerte (para Apriori)
  - Agua: se compra en ~45% de las órdenes sin importar nada (trampa: confianza alta, lift ~1)
"""
import numpy as np, pandas as pd
rng = np.random.default_rng(2026)

cust = pd.read_csv("../semana1/data/customers.csv", parse_dates=["signup_date","last_active_date"])
N = len(cust)

items = pd.DataFrame([
 ("Latte","Bebida",5.25,0.70),("Cappuccino","Bebida",4.95,0.70),("Americano","Bebida",3.75,0.75),
 ("Cold Brew","Bebida",4.95,0.72),("Té Chai","Bebida",4.75,0.68),("Frappuccino","Bebida",6.25,0.66),
 ("Matcha Latte","Bebida",5.75,0.68),("Espresso","Bebida",3.25,0.78),("Chocolate Caliente","Bebida",4.65,0.66),
 ("Té Verde","Bebida",3.45,0.74),("Refresher","Bebida",5.45,0.64),("Flat White","Bebida",5.15,0.70),
 ("Agua","Bebida",2.25,0.60),
 ("Croissant","Comida",3.95,0.55),("Muffin","Comida",3.75,0.55),("Banana Bread","Comida",3.65,0.55),
 ("Sándwich","Comida",7.25,0.45),("Ensalada","Comida",8.25,0.45),("Galleta","Comida",2.95,0.60),
 ("Pastel de Queso","Comida",4.95,0.50),("Granola","Comida",4.25,0.50),("Copa de Fruta","Comida",4.45,0.50),
 ("Bagel","Comida",3.45,0.58),("Wrap","Comida",6.95,0.46),("Brownie","Comida",3.55,0.58),
 ("Yogur","Comida",3.95,0.52),("Panini","Comida",7.45,0.45),("Scone","Comida",3.65,0.56),("Dona","Comida",2.75,0.62),
], columns=["item","categoria","precio","margen"])
names = items["item"].tolist(); ix = {n:i for i,n in enumerate(names)}
cat = items.set_index("item")["categoria"]
bev = [n for n in names if cat[n]=="Bebida" and n!="Agua"]
food = [n for n in names if cat[n]=="Comida"]

groups = {
 "Dulce clásico": {"Latte":3,"Cappuccino":2,"Croissant":3,"Muffin":3,"Scone":2,"Dona":2},
 "Fit":           {"Cold Brew":3,"Matcha Latte":3,"Ensalada":3,"Granola":3,"Copa de Fruta":3,"Yogur":2},
 "Ejecutivo":     {"Americano":3,"Espresso":2,"Flat White":2,"Sándwich":3,"Panini":3,"Wrap":2,"Bagel":2},
 "Joven frío":    {"Frappuccino":3,"Refresher":3,"Galleta":3,"Pastel de Queso":3,"Brownie":2,"Dona":1},
 "Té y pan":      {"Té Chai":4,"Té Verde":3,"Banana Bread":3,"Scone":1,"Croissant":1,"Muffin":1},
 "Chocolate":     {"Chocolate Caliente":4,"Brownie":3,"Galleta":2,"Banana Bread":1,"Muffin":1},
}
G = np.zeros((len(groups), len(names)))
for g,(k,d) in enumerate(groups.items()):
    for n,w in d.items(): G[g,ix[n]] = w
G = G/G.sum(1,keepdims=True)

# Asociaciones bebida -> comida (multiplicador sobre el gusto del cliente)
ASSOC = {("Latte","Croissant"):6, ("Cappuccino","Muffin"):5, ("Matcha Latte","Granola"):5,
         ("Frappuccino","Galleta"):6, ("Americano","Sándwich"):5, ("Té Chai","Banana Bread"):4}
P_FOOD = 0.55   # prob. base de que la orden lleve comida
P_AGUA = 0.45   # prob. independiente de agregar agua

# gusto de cada cliente = mezcla de 1-2 grupos (dominante + ruido)
dom = rng.integers(0,len(groups),N)
mix = np.full((N,len(groups)),0.01)
mix[np.arange(N),dom] = 1.0
sec = rng.integers(0,len(groups),N); mix[np.arange(N),sec] += rng.uniform(0,0.35,N)
mix /= mix.sum(1,keepdims=True)
taste = mix @ G                       # N x items
# cada cliente solo "conoce" un subconjunto de su gusto: sparsifica
taste *= rng.random((N,len(names)))<0.85
taste += 2e-4

# fechas: reutilizamos el rango de la base (2024-09-02 .. 2026-08-30)
d0, d1 = pd.Timestamp("2024-09-02"), pd.Timestamp("2026-08-30")
rows=[]; oid=0
rate = rng.gamma(1.4, 5.0, N).clip(1,60)   # nº de órdenes por cliente (2 años)
for c in range(N):
    n_ord = max(2, int(rng.poisson(rate[c])))
    start = max(d0, cust.loc[c,"signup_date"]) if cust.loc[c,"signup_date"]>d0 else d0
    span = (d1-start).days
    if span<1: continue
    days = np.sort(rng.integers(0,span+1,n_ord))
    for d in days:
        oid+=1; date = start+pd.Timedelta(days=int(d))
        wb = np.array([taste[c,ix[b]] for b in bev]); b = rng.choice(bev,p=wb/wb.sum())
        basket=[b]
        if rng.random()<P_FOOD:
            wf = np.array([taste[c,ix[f]]*ASSOC.get((b,f),1.0) for f in food])
            basket.append(rng.choice(food,p=wf/wf.sum()))
        if rng.random()<P_AGUA: basket.append("Agua")
        for it in basket: rows.append((oid,int(cust.loc[c,"customer_id"]),date.date(),it))
orders = pd.DataFrame(rows,columns=["order_id","customer_id","order_date","item"])
orders.to_csv("data/orders.csv",index=False)
items.to_csv("data/items.csv",index=False)
cust[["customer_id","segment","city","signup_date"]].to_csv("data/customers.csv",index=False)
print(orders.shape, orders.order_id.nunique(), orders.customer_id.nunique())
print(orders.item.value_counts(normalize=False).div(orders.order_id.nunique()).round(3))
