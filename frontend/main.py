from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
import requests
import webbrowser

API_URL = "http://127.0.0.1:5000"

# Ejemplo para mostrar un popup que se cierra solo
def show_auto_dismiss_popup(title, message, duration=1):
    popup = Popup(title=title, content=Label(text=message), size_hint=(0.5, 0.5))
    popup.open()
    Clock.schedule_once(lambda dt: popup.dismiss(), duration)
    return popup

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='Email'))
        self.email = TextInput(multiline=False)
        layout.add_widget(self.email)
        layout.add_widget(Label(text='Password'))
        self.password = TextInput(password=True, multiline=False)
        layout.add_widget(self.password)
        layout.add_widget(Button(text='Iniciar sesión', on_press=self.login))
        layout.add_widget(Button(text='Crear cuenta', on_press=self.register))
        layout.add_widget(Button(text='Iniciar sesión con Google', on_press=self.login_google))
        self.add_widget(layout)

    def login(self, instance):
        data = {'email': self.email.text, 'password': self.password.text}
        r = requests.post(f"{API_URL}/login", json=data)
        if r.status_code == 200:
            self.manager.current = 'products'
            self.manager.get_screen('products').load_products()
        else:
            show_auto_dismiss_popup('Error', 'Credenciales incorrectas')

    def register(self, instance):
        data = {'username': self.email.text, 'email': self.email.text, 'password': self.password.text}
        r = requests.post(f"{API_URL}/register", json=data)
        if r.status_code == 201:
            show_auto_dismiss_popup('Éxito', 'Usuario creado')
        else:
            show_auto_dismiss_popup('Error', 'No se pudo crear usuario')

    def login_google(self, instance):
        show_auto_dismiss_popup('Google OAUTH', 'Simulación de OAUTH Google')

class ProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = []
        self.layout = BoxLayout(orientation='vertical')
        self.scroll = ScrollView()
        self.products_box = BoxLayout(orientation='vertical', size_hint_y=None)
        self.products_box.bind(minimum_height=self.products_box.setter('height'))
        self.scroll.add_widget(self.products_box)
        self.layout.add_widget(Label(text='Productos disponibles', font_size=22))
        self.layout.add_widget(self.scroll)
        self.layout.add_widget(Button(text='Ver carrito', on_press=self.go_cart, size_hint_y=None, height=40))
        self.layout.add_widget(Button(text='Modo vendedor', on_press=self.go_seller, size_hint_y=None, height=40))
        self.layout.add_widget(Button(text='Chatbot', on_press=self.go_chatbot, size_hint_y=None, height=40))
        self.add_widget(self.layout)

    def load_products(self):
        self.products_box.clear_widgets()
        # Obtener productos
        r = requests.get(f"{API_URL}/products")
        products = r.json() if r.status_code == 200 else []
        # Obtener categorías para mostrar el nombre en el popup
        r_cat = requests.get(f"{API_URL}/categories")
        categories = r_cat.json() if r_cat.status_code == 200 else []
        cat_dict = {cat['CategoryID']: cat['Name'] for cat in categories}
        for prod in products:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            box.add_widget(Label(text=prod['Name']))
            box.add_widget(Label(text=f"${prod['Price']}"))
            add_btn = Button(text='Agregar al carrito', size_hint_x=None, width=140)
            add_btn.bind(on_press=lambda inst, p=prod: self.add_to_cart(p))
            details_btn = Button(text='Ver detalles', size_hint_x=None, width=120)
            details_btn.bind(on_press=lambda inst, p=prod: self.show_details(p, cat_dict))
            box.add_widget(add_btn)
            box.add_widget(details_btn)
            self.products_box.add_widget(box)

    def show_details(self, product, cat_dict):
        # Obtener reseñas
        r = requests.get(f"{API_URL}/reviews/{product['ProductID']}")
        reviews = r.json() if r.status_code == 200 else []
        review_text = "\n".join([f"⭐{rev['Rating']}: {rev['Comment']}" for rev in reviews]) or "Sin reseñas"
        categoria = cat_dict.get(product['CategoryID'], "Sin categoría")
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=f"[b]{product['Name']}[/b]\n\nCategoría: {categoria}\n\n{product['Description']}", markup=True))
        content.add_widget(Label(text=f"\n[b]Reseñas:[/b]\n{review_text}", markup=True))
        popup = Popup(title='Detalles del producto', content=content, size_hint=(0.7, 0.7))
        popup.open()

    def add_to_cart(self, product):
        self.cart.append(product)
        show_auto_dismiss_popup('Carrito', 'Producto agregado al carrito')

    def go_cart(self, instance):
        self.manager.get_screen('cart').update_cart(self.cart)
        self.manager.current = 'cart'

    def go_seller(self, instance):
        self.manager.current = 'seller'

    def go_chatbot(self, instance):
        self.manager.current = 'chatbot'

class SellerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_product = None
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.form_box = BoxLayout(orientation='vertical', size_hint_y=None, height=350, spacing=8)
        self.form_box.add_widget(Label(text='Nombre', font_size=20))
        self.name_input = TextInput(font_size=20, size_hint_y=None, height=40)
        self.form_box.add_widget(self.name_input)
        self.form_box.add_widget(Label(text='Descripción', font_size=20))
        self.desc_input = TextInput(font_size=20, size_hint_y=None, height=80)
        self.form_box.add_widget(self.desc_input)
        self.form_box.add_widget(Label(text='Precio', font_size=20))
        self.price_input = TextInput(font_size=20, size_hint_y=None, height=40)
        self.form_box.add_widget(self.price_input)
        self.form_box.add_widget(Label(text='Stock', font_size=20))
        self.stock_input = TextInput(font_size=20, size_hint_y=None, height=40)
        self.form_box.add_widget(self.stock_input)
        self.form_box.add_widget(Label(text='ID Categoría', font_size=20))
        self.cat_input = TextInput(font_size=20, size_hint_y=None, height=40)
        self.form_box.add_widget(self.cat_input)
        self.save_btn = Button(text='Agregar producto', on_press=self.save_product, size_hint_y=None, height=40)
        self.form_box.add_widget(self.save_btn)
        self.layout.add_widget(self.form_box)

        self.products_box = BoxLayout(orientation='vertical', size_hint_y=None)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.products_box.bind(minimum_height=self.products_box.setter('height'))
        self.scroll.add_widget(self.products_box)
        self.layout.add_widget(Label(text='Tus productos', font_size=20))
        self.layout.add_widget(self.scroll)
        self.layout.add_widget(Button(text='Volver', on_press=self.go_back, size_hint_y=None, height=50))
        self.add_widget(self.layout)

    def on_pre_enter(self):
        self.load_products()
        self.clear_form()

    def clear_form(self):
        self.selected_product = None
        self.name_input.text = ''
        self.desc_input.text = ''
        self.price_input.text = ''
        self.stock_input.text = ''
        self.cat_input.text = ''
        self.save_btn.text = 'Agregar producto'

    def load_products(self):
        self.products_box.clear_widgets()
        # Aquí deberías filtrar por SellerID, pero para demo se muestran todos
        r = requests.get(f"{API_URL}/products")
        if r.status_code == 200:
            for prod in r.json():
                box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                box.add_widget(Label(text=prod['Name']))
                box.add_widget(Label(text=f"${prod['Price']}"))
                edit_btn = Button(text='Editar', size_hint_x=None, width=80)
                edit_btn.bind(on_press=lambda inst, p=prod: self.edit_product(p))
                box.add_widget(edit_btn)
                self.products_box.add_widget(box)

    def save_product(self, instance):
        name = self.name_input.text.strip()
        desc = self.desc_input.text.strip()
        price = self.price_input.text.strip()
        stock = self.stock_input.text.strip()
        cat = self.cat_input.text.strip()
        if not (name and price and stock and cat):
            show_auto_dismiss_popup('Error', 'Completa todos los campos obligatorios')
            return
        try:
            price = float(price)
            stock = int(stock)
            cat = int(cat)
        except:
            show_auto_dismiss_popup('Error', 'Precio, stock y categoría deben ser numéricos')
            return

        # Simula SellerID y usuario_creacion
        seller_id = 1
        usuario = "admin"

        data = {
            'seller_id': seller_id,
            'name': name,
            'description': desc,
            'price': price,
            'stock': stock,
            'category_id': cat,
            'usuario_creacion': usuario,
            'usuario_modificacion': usuario
        }

        if self.selected_product:
            # Modificar producto
            prod_id = self.selected_product['ProductID']
            r = requests.put(f"{API_URL}/products/{prod_id}", json=data)
            if r.status_code == 200:
                show_auto_dismiss_popup('Éxito', 'Producto modificado')
                self.clear_form()
                self.load_products()
            else:
                show_auto_dismiss_popup('Error', 'No se pudo modificar')
        else:
            # Agregar producto
            r = requests.post(f"{API_URL}/products", json=data)
            if r.status_code == 201:
                show_auto_dismiss_popup('Éxito', 'Producto agregado')
                self.clear_form()
                self.load_products()
            else:
                show_auto_dismiss_popup('Error', 'No se pudo agregar')

    def edit_product(self, prod):
        self.selected_product = prod
        self.name_input.text = prod['Name']
        self.desc_input.text = prod['Description'] or ''
        self.price_input.text = str(prod['Price'])
        self.stock_input.text = str(prod['Stock'])
        self.cat_input.text = str(prod['CategoryID'])
        self.save_btn.text = 'Guardar cambios'

    def go_back(self, instance):
        self.manager.current = 'products'

class ChatbotScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Soporte Chatbot'))
        layout.add_widget(Button(text='Abrir Chatbot', on_press=self.open_chatbot))
        layout.add_widget(Button(text='Volver', on_press=self.go_back))
        self.add_widget(layout)

    def open_chatbot(self, instance):
        webbrowser.open("https://widget.kommunicate.io/chat?appId=2020521d2025ab5eaa00a302db60492de")

    def go_back(self, instance):
        self.manager.current = 'products'

class CartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.cart_box = BoxLayout(orientation='vertical', size_hint_y=None)
        self.scroll = ScrollView()
        self.cart_box.bind(minimum_height=self.cart_box.setter('height'))
        self.scroll.add_widget(self.cart_box)
        self.layout.add_widget(Label(text='Carrito de compras'))
        self.layout.add_widget(self.scroll)
        self.layout.add_widget(Button(text='Volver', on_press=self.go_back))
        self.add_widget(self.layout)
        self.cart = []

    def update_cart(self, cart):
        self.cart = cart
        self.cart_box.clear_widgets()
        for idx, prod in enumerate(self.cart):
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            box.add_widget(Label(text=prod['Name']))
            box.add_widget(Label(text=f"${prod['Price']}"))
            del_btn = Button(text='Eliminar')
            del_btn.bind(on_press=lambda inst, i=idx: self.remove_from_cart(i))
            box.add_widget(del_btn)
            self.cart_box.add_widget(box)

    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            del self.cart[index]
            self.update_cart(self.cart)

    def go_back(self, instance):
        self.manager.current = 'products'

class PlantasiaApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ProductScreen(name='products'))
        sm.add_widget(SellerScreen(name='seller'))
        sm.add_widget(ChatbotScreen(name='chatbot'))
        sm.add_widget(CartScreen(name='cart'))
        return sm

if __name__ == '__main__':
    PlantasiaApp().run()