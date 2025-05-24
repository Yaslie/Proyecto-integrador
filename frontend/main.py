from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
import requests
import webbrowser

API_URL = "http://127.0.0.1:5000"

# Paleta de colores
PRIMARY = "#4CAF50"      # Verde principal
SECONDARY = "#A5D6A7"    # Verde claro
BACKGROUND = "#F5FFF5"   # Blanco verdoso
TEXT = "#222222"         # Gris oscuro

def style_widget(widget, bg=BACKGROUND, radius=16):
    with widget.canvas.before:
        Color(*get_rgb(bg))
        widget.rect = RoundedRectangle(radius=[radius], pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda w, v: setattr(widget.rect, 'pos', widget.pos))
    widget.bind(size=lambda w, v: setattr(widget.rect, 'size', widget.size))

def get_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    return tuple(int(hex_color[i:i + lv // 3], 16)/255.0 for i in range(0, lv, lv // 3))

def show_auto_dismiss_popup(title, message, duration=1):
    content = BoxLayout(orientation='vertical', padding=20, spacing=10)
    lbl = Label(text=message, font_size=18)
    content.add_widget(lbl)
    popup = Popup(title=title, content=content, size_hint=(0.5, 0.3))
    Clock.schedule_once(lambda dt: popup.dismiss(), duration)
    popup.open()
    return popup

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Fondo verde suave
        with self.canvas.before:
            Color(*get_rgb("#C7D8B6"))  # Verde pastel
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Caja central blanca
        main_box = BoxLayout(orientation='vertical', padding=40, spacing=18, size_hint=(None, None), width=380, height=450, pos_hint={'center_x':0.5, 'center_y':0.5})
        with main_box.canvas.before:
            Color(1, 1, 1, 1)
            main_box.rect = RoundedRectangle(radius=[32], pos=main_box.pos, size=main_box.size)
        main_box.bind(pos=lambda w, v: setattr(main_box.rect, 'pos', main_box.pos))
        main_box.bind(size=lambda w, v: setattr(main_box.rect, 'size', main_box.size))

        # Logo o título
        main_box.add_widget(Label(text='[b]Plantasia[/b]', markup=True, font_size=28, color=get_rgb(TEXT), size_hint_y=None, height=40, halign='center', valign='middle'))

        # Subtítulo
        main_box.add_widget(Label(text='INICIA SESIÓN', font_size=22, color=get_rgb(TEXT), bold=True, size_hint_y=None, height=32, halign='center', valign='middle'))

        # Campo de correo
        self.email = TextInput(hint_text='Correo / Número telefónico', multiline=False, font_size=16, size_hint_y=None, height=40, background_color=(1,1,1,1), foreground_color=get_rgb(TEXT), padding=[10,10,10,10])
        self.email.background_normal = ''
        self.email.background_active = ''
        main_box.add_widget(self.email)

        # Campo de contraseña
        self.password = TextInput(hint_text='Contraseña', password=True, multiline=False, font_size=16, size_hint_y=None, height=40, background_color=(1,1,1,1), foreground_color=get_rgb(TEXT), padding=[10,10,10,10])
        self.password.background_normal = ''
        self.password.background_active = ''
        main_box.add_widget(self.password)

        # Botón de entrar
        btn_login = Button(text='Entrar', font_size=18, size_hint_y=None, height=40, background_normal='', background_color=get_rgb("#B7D7A8"), color=(1,1,1,1), bold=True)
        btn_login.bind(on_press=self.login)
        main_box.add_widget(btn_login)

        # Botón de Google
        btn_google = Button(text='Iniciar sesión con Google', font_size=16, size_hint_y=None, height=38, background_normal='', background_color=get_rgb("#F5FFF5"), color=get_rgb(PRIMARY))
        btn_google.bind(on_press=self.login_google)
        main_box.add_widget(btn_google)

        # Botón de crear cuenta
        btn_register = Button(text='Crear cuenta', font_size=16, size_hint_y=None, height=38, background_normal='', background_color=get_rgb("#F5FFF5"), color=get_rgb(PRIMARY))
        btn_register.bind(on_press=self.register)
        main_box.add_widget(btn_register)

        self.add_widget(main_box)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def login(self, instance):
        data = {'email': self.email.text, 'password': self.password.text}
        r = requests.post(f"{API_URL}/login", json=data)
        if r.status_code == 200:
            self.manager.current = 'products'
            self.manager.get_screen('products').load_products()
        else:
            show_auto_dismiss_popup('Error', 'Credenciales incorrectas')

    def login_google(self, instance):
        show_auto_dismiss_popup('Google OAUTH', 'Simulación de OAUTH Google')

    def register(self, instance):
        email = self.email.text.strip()
        password = self.password.text.strip()
        if not email or not password:
            show_auto_dismiss_popup('Error', 'Completa todos los campos')
            return
        data = {'username': email, 'email': email, 'password': password}
        r = requests.post(f"{API_URL}/register", json=data)
        if r.status_code == 201:
            show_auto_dismiss_popup('Éxito', 'Usuario creado')
        else:
            show_auto_dismiss_popup('Error', 'No se pudo crear usuario')

class ProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = []
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.layout.add_widget(Label(text='[b]Productos disponibles[/b]', markup=True, font_size=24, color=get_rgb(PRIMARY)))
        self.scroll = ScrollView()
        self.products_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.products_box.bind(minimum_height=self.products_box.setter('height'))
        self.scroll.add_widget(self.products_box)
        self.layout.add_widget(self.scroll)
        btns = BoxLayout(orientation='horizontal', size_hint_y=None, height=85, spacing=15, padding=10)
        btn_carrito = Button(text='Ver carrito', font_size=16, on_press=self.go_cart)
        btn_carrito.background_color = get_rgb(PRIMARY)
        btn_carrito.color = get_rgb(BACKGROUND)
        btns.add_widget(btn_carrito)

        btn_vendedor = Button(text='Modo vendedor', font_size=16, on_press=self.go_seller)
        btn_vendedor.background_color = get_rgb(SECONDARY)
        btn_vendedor.color = get_rgb(TEXT)
        btns.add_widget(btn_vendedor)

        btn_chatbot = Button(text='Chatbot', font_size=16, on_press=self.go_chatbot)
        btn_chatbot.background_color = get_rgb(BACKGROUND)
        btn_chatbot.color = get_rgb(PRIMARY)
        btns.add_widget(btn_chatbot)
        self.layout.add_widget(btns)
        self.add_widget(self.layout)
        style_widget(self.layout, bg=BACKGROUND, radius=0)

    def load_products(self):
        self.products_box.clear_widgets()
        r = requests.get(f"{API_URL}/products")
        products = r.json() if r.status_code == 200 else []
        r_cat = requests.get(f"{API_URL}/categories")
        categories = r_cat.json() if r_cat.status_code == 200 else []
        cat_dict = {cat['CategoryID']: cat['Name'] for cat in categories}
        for prod in products:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=12, padding=8)
            box.add_widget(Label(text=prod['Name'], size_hint_x=0.35, font_size=18, color=get_rgb(TEXT)))
            box.add_widget(Label(text=f"${prod['Price']}", size_hint_x=0.18, font_size=18, color=get_rgb(TEXT)))
            add_btn = Button(text='Agregar al carrito', size_hint_x=0.32, width=180, background_color=get_rgb(PRIMARY), color=get_rgb(BACKGROUND), font_size=16)
            add_btn.bind(on_press=lambda inst, p=prod: self.add_to_cart(p))
            box.add_widget(add_btn)
            from kivy.uix.widget import Widget
            box.add_widget(Widget(size_hint_x=0.03))
            details_btn = Button(text='Ver detalles', size_hint_x=0.12, width=100, background_color=get_rgb(SECONDARY), color=get_rgb(TEXT), font_size=16)
            details_btn.bind(on_press=lambda inst, p=prod: self.show_details(p, cat_dict))
            box.add_widget(details_btn)
            style_widget(box, bg=SECONDARY, radius=12)
            self.products_box.add_widget(box)

    def show_details(self, product, cat_dict):
        r = requests.get(f"{API_URL}/reviews/{product['ProductID']}")
        reviews = r.json() if r.status_code == 200 else []
        review_text = "\n".join([f"⭐{rev['Rating']}: {rev['Comment']}" for rev in reviews]) or "Sin reseñas"
        categoria = cat_dict.get(product['CategoryID'], "Sin categoría")
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        content.add_widget(Label(text=f"[b]{product['Name']}[/b]\n\nCategoría: {categoria}\n\n{product['Description']}", markup=True, font_size=18, color=get_rgb(TEXT)))
        content.add_widget(Label(text=f"\n[b]Reseñas:[/b]\n{review_text}", markup=True, font_size=16, color=get_rgb(TEXT)))
        popup = Popup(title='Detalles del producto', content=content, size_hint=(0.7, 0.7), background_color=get_rgb(BACKGROUND))
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
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.form_box = BoxLayout(orientation='vertical', size_hint_y=None, height=350, spacing=10)
        self.form_box.add_widget(Label(text='Nombre', font_size=18, color=get_rgb(TEXT)))
        self.name_input = TextInput(font_size=18, size_hint_y=None, height=40, background_color=SECONDARY, foreground_color=TEXT)
        self.form_box.add_widget(self.name_input)
        self.form_box.add_widget(Label(text='Descripción', font_size=18, color=get_rgb(TEXT)))
        self.desc_input = TextInput(font_size=18, size_hint_y=None, height=80, background_color=SECONDARY, foreground_color=TEXT)
        self.form_box.add_widget(self.desc_input)
        self.form_box.add_widget(Label(text='Precio', font_size=18, color=get_rgb(TEXT)))
        self.price_input = TextInput(font_size=18, size_hint_y=None, height=40, background_color=SECONDARY, foreground_color=TEXT)
        self.form_box.add_widget(self.price_input)
        self.form_box.add_widget(Label(text='Stock', font_size=18, color=get_rgb(TEXT)))
        self.stock_input = TextInput(font_size=18, size_hint_y=None, height=40, background_color=SECONDARY, foreground_color=TEXT)
        self.form_box.add_widget(self.stock_input)
        self.form_box.add_widget(Label(text='ID Categoría', font_size=18, color=get_rgb(TEXT)))
        self.cat_input = TextInput(font_size=18, size_hint_y=None, height=40, background_color=SECONDARY, foreground_color=TEXT)
        self.form_box.add_widget(self.cat_input)
        self.save_btn = Button(text='Agregar producto', on_press=self.save_product, size_hint_y=None, height=45, background_color=get_rgb(PRIMARY), color=get_rgb(BACKGROUND), font_size=18)
        self.form_box.add_widget(self.save_btn)
        self.layout.add_widget(self.form_box)
        self.layout.add_widget(Label(text='Tus productos', font_size=20, color=get_rgb(PRIMARY)))
        self.products_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.products_box.bind(minimum_height=self.products_box.setter('height'))
        self.scroll.add_widget(self.products_box)
        self.layout.add_widget(self.scroll)
        self.layout.add_widget(Button(text='Volver', on_press=self.go_back, size_hint_y=None, height=50, background_color=get_rgb(SECONDARY), color=get_rgb(TEXT), font_size=18))
        self.add_widget(self.layout)
        style_widget(self.layout, bg=BACKGROUND, radius=0)

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
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text='Soporte Chatbot', font_size=22, color=get_rgb(PRIMARY)))
        layout.add_widget(Button(text='Abrir Chatbot', on_press=self.open_chatbot, background_color=get_rgb(PRIMARY), color=get_rgb(BACKGROUND), font_size=18, size_hint_y=None, height=45))
        layout.add_widget(Button(text='Volver', on_press=self.go_back, background_color=get_rgb(SECONDARY), color=get_rgb(TEXT), font_size=18, size_hint_y=None, height=45))
        self.add_widget(layout)
        style_widget(layout, bg=BACKGROUND, radius=0)

    def open_chatbot(self, instance):
        webbrowser.open("https://widget.kommunicate.io/chat?appId=2020521d2025ab5eaa00a302db60492de")

    def go_back(self, instance):
        self.manager.current = 'products'

class CartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.layout.add_widget(Label(text='Carrito de compras', font_size=22, color=get_rgb(PRIMARY)))
        self.cart_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.scroll = ScrollView()
        self.cart_box.bind(minimum_height=self.cart_box.setter('height'))
        self.scroll.add_widget(self.cart_box)
        self.layout.add_widget(self.scroll)
        self.total_label = Label(text='Total: $0.00', font_size=18, color=get_rgb(TEXT))
        self.layout.add_widget(self.total_label)
        self.layout.add_widget(Button(text='Volver', on_press=self.go_back, background_color=get_rgb(SECONDARY), color=get_rgb(TEXT), font_size=18, size_hint_y=None, height=45))
        self.add_widget(self.layout)
        self.cart = []
        style_widget(self.layout, bg=BACKGROUND, radius=0)

    def update_cart(self, cart):
        self.cart = cart
        self.cart_box.clear_widgets()
        total = 0
        for idx, prod in enumerate(self.cart):
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            box.add_widget(Label(text=prod['Name']))
            box.add_widget(Label(text=f"${prod['Price']}"))
            del_btn = Button(text='Eliminar')
            del_btn.bind(on_press=lambda inst, i=idx: self.remove_from_cart(i))
            box.add_widget(del_btn)
            self.cart_box.add_widget(box)
            try:
                total += float(prod['Price'])
            except Exception:
                pass
        self.total_label.text = f"Total: ${total:.2f}"

    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            del self.cart[index]
            self.update_cart(self.cart)

    def go_back(self, instance):
        self.manager.current = 'products'

class PlantasiaApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.3))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ProductScreen(name='products'))
        sm.add_widget(SellerScreen(name='seller'))
        sm.add_widget(ChatbotScreen(name='chatbot'))
        sm.add_widget(CartScreen(name='cart'))
        return sm

if __name__ == '__main__':
    PlantasiaApp().run()

