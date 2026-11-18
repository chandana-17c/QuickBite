from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal, ROUND_HALF_UP
from typing import List
from uuid import uuid4
import hashlib

app = FastAPI(title="QuickBite API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
MENU = [
 {"id":1,"name":"Classic Smash Burger","description":"Double smash patty, cheddar, house sauce","category":"Burgers","price":Decimal("249.00"),"image":"https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=700","veg":False},
 {"id":2,"name":"Crispy Chicken Burger","description":"Golden chicken, slaw and spicy mayo","category":"Burgers","price":Decimal("229.00"),"image":"https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=700","veg":False},
 {"id":3,"name":"Margherita Pizza","description":"San Marzano tomato, mozzarella, basil","category":"Pizza","price":Decimal("299.00"),"image":"https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=700","veg":True},
 {"id":4,"name":"Farmhouse Pizza","description":"Roasted peppers, onion, olives, mozzarella","category":"Pizza","price":Decimal("379.00"),"image":"https://images.unsplash.com/photo-1513104890138-7c749659a591?w=700","veg":True},
 {"id":5,"name":"Paneer Tikka Bowl","description":"Charred paneer, rice, mint yogurt","category":"Bowls","price":Decimal("269.00"),"image":"https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=700","veg":True},
 {"id":6,"name":"Teriyaki Chicken Bowl","description":"Grilled chicken, sesame rice, greens","category":"Bowls","price":Decimal("319.00"),"image":"https://images.unsplash.com/photo-1547592180-85f173990554?w=700","veg":False},
 {"id":7,"name":"Truffle Mushroom Pasta","description":"Creamy parmesan sauce and wild mushrooms","category":"Pasta","price":Decimal("329.00"),"image":"https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=700","veg":True},
 {"id":8,"name":"Penne Arrabbiata","description":"Tomato, garlic, chilli and fresh herbs","category":"Pasta","price":Decimal("279.00"),"image":"https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=700","veg":True},
 {"id":9,"name":"Loaded Masala Fries","description":"Crispy fries, chaat masala, creamy dip","category":"Sides","price":Decimal("149.00"),"image":"https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=700","veg":True},
 {"id":10,"name":"Garlic Parmesan Bites","description":"Warm dough bites with garlic butter","category":"Sides","price":Decimal("169.00"),"image":"https://images.unsplash.com/photo-1585238342024-78d387f4a707?w=700","veg":True},
 {"id":11,"name":"Mango Lassi","description":"Chilled Alphonso mango and yogurt","category":"Drinks","price":Decimal("99.00"),"image":"https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=700","veg":True},
 {"id":12,"name":"Chocolate Brownie","description":"Warm fudge brownie, dark chocolate","category":"Desserts","price":Decimal("129.00"),"image":"https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=700","veg":True},
]
users = {"demo@quickbite.in": {"name":"QuickBite Demo","password_hash":hashlib.sha256(b"QuickBite123!").hexdigest()}}
def money(v): return Decimal(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
class Credentials(BaseModel):
 name: str = Field(min_length=1, max_length=80)
 email: EmailStr
 password: str = Field(min_length=8, max_length=128)
class Login(BaseModel):
 email: EmailStr
 password: str = Field(min_length=1, max_length=128)
class Line(BaseModel):
 item_id: int = Field(gt=0)
 quantity: int = Field(ge=0, le=1000)
class Cart(BaseModel): items: List[Line]
class Calculation(Cart): coupon: str | None = None
class Checkout(Calculation):
 customer_name: str = Field(min_length=1, max_length=80)
 email: EmailStr
 address: str = Field(min_length=8, max_length=300)
def calculate(data):
 if not data.items: raise HTTPException(422, "Cart must contain at least one item")
 subtotal=Decimal("0.00"); lines=[]
 for line in data.items:
  if line.quantity < 1: raise HTTPException(422, "Quantity must be at least 1")
  product=next((x for x in MENU if x["id"]==line.item_id),None)
  if product is None: raise HTTPException(422, f"Unknown item_id: {line.item_id}")
  row=money(product["price"]*line.quantity); subtotal+=row
  lines.append({"item_id":product["id"],"name":product["name"],"quantity":line.quantity,"unit_price":str(product["price"]),"line_total":str(row)})
 subtotal=money(subtotal)
 if subtotal < 100: raise HTTPException(422, "Minimum order subtotal is INR 100.00")
 code=(getattr(data, "coupon", None) or "").strip().upper(); discount=Decimal("0.00")
 if code:
  if code=="QUICK10": discount=money(subtotal*Decimal("0.10"))
  elif code=="SAVE50": discount=min(Decimal("50.00"),subtotal)
  else: raise HTTPException(422, "Invalid coupon code")
 discounted=money(subtotal-discount); delivery=Decimal("0.00") if subtotal>=499 else Decimal("40.00"); tax=money(discounted*Decimal("0.05")); total=money(discounted+delivery+tax)
 return {"items":lines,"subtotal":str(subtotal),"coupon":code or None,"discount":str(discount),"discounted_subtotal":str(discounted),"delivery_fee":str(delivery),"tax":str(tax),"total":str(total)}
@app.get("/api/health")
def health(): return {"status":"ok","service":"QuickBite API"}
@app.post("/api/auth/register",status_code=201)
def register(body:Credentials):
 email=body.email.lower()
 if email in users: raise HTTPException(409,"Email already registered")
 users[email]={"name":body.name,"password_hash":hashlib.sha256(body.password.encode()).hexdigest()}
 return {"token":"demo-"+uuid4().hex,"name":body.name,"email":email}
@app.post("/api/auth/login")
def login(body:Login):
 user=users.get(body.email.lower())
 if not user or user["password_hash"]!=hashlib.sha256(body.password.encode()).hexdigest(): raise HTTPException(401,"Invalid email or password")
 return {"token":"demo-"+uuid4().hex,"name":user["name"],"email":body.email.lower()}
@app.get("/api/menu")
def menu(): return [{**x,"price":str(x["price"])} for x in MENU]
@app.get("/api/menu/{item_id}")
def menu_item(item_id:int):
 item=next((x for x in MENU if x["id"]==item_id),None)
 if not item: raise HTTPException(404,"Menu item not found")
 return {**item,"price":str(item["price"])}
@app.post("/api/cart/validate")
def validate_cart(body:Cart): return calculate(body)
@app.post("/api/orders/calculate")
def order_calculate(body:Calculation): return calculate(body)
@app.post("/api/orders/checkout",status_code=201)
def checkout(body:Checkout): return {"order_id":"QB-"+uuid4().hex[:10].upper(),"customer_name":body.customer_name,"email":body.email,**calculate(body)}
