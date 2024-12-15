from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from random import randint, shuffle

Base = declarative_base()

class Warehouse(Base):
    __tablename__ = 'warehouse'

    warehouse_id = Column(Integer, primary_key=True)
    location = Column(String, nullable=False, name="Where")
    inventories = relationship('Inventory', back_populates='warehouse')

class Inventory(Base):
    __tablename__ = 'inventory'

    inventory_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    result = Column(Text, nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouse.warehouse_id', ondelete='CASCADE'), nullable=False)

    warehouse = relationship('Warehouse', back_populates='inventories')
    warehouse_products = relationship('WarehouseProducts', back_populates='inventory')

class Product(Base):
    __tablename__ = 'product'

    product_id = Column(Integer, primary_key=True)
    product_name = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    warehouse_products = relationship('WarehouseProducts', back_populates='product')

class WarehouseProducts(Base):
    __tablename__ = 'warehouse_products'

    inventory_id = Column(Integer, ForeignKey('inventory.inventory_id', ondelete='CASCADE'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.product_id', ondelete='CASCADE'), primary_key=True)

    inventory = relationship('Inventory', back_populates='warehouse_products')
    product = relationship('Product', back_populates='warehouse_products')

class Model:
    def __init__(self):
        self.engine = create_engine('postgresql://postgres:1111@localhost:5432/postgres')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_line_Warehouse(self, Where):
        warehouse = Warehouse(location=Where)
        self.session.add(warehouse)
        self.session.commit()

    def add_line_Inventory(self, User_id, Result, Warehouse_id):
        warehouse = self.session.query(Warehouse).filter_by(warehouse_id=Warehouse_id).first()
        if not warehouse:
            print(f"Error: Warehouse_id {Warehouse_id} does not exist.")
            return 0
        inventory = Inventory(user_id=User_id, result=Result, warehouse_id=Warehouse_id)
        self.session.add(inventory)
        self.session.commit()

    def add_line_Product(self, Product_Name, Quantity):
        product = Product(product_name=Product_Name, quantity=Quantity)
        self.session.add(product)
        self.session.commit()

    def add_line_Warehouse_Products(self, Inventory_id, Product_id):
        inventory = self.session.query(Inventory).filter_by(inventory_id=Inventory_id).first()
        product = self.session.query(Product).filter_by(product_id=Product_id).first()
        if not inventory:
            print(f"Error: Inventory {Inventory_id} does not exist.")
            return 0
        if not product:
            print(f"Error: Product_id {Product_id} does not exist.")
            return 0
        wp = WarehouseProducts(inventory_id=Inventory_id, product_id=Product_id)
        self.session.add(wp)
        self.session.commit()

    def get_all_line(self, choice_table):
        if choice_table == 1:
            return [(w.warehouse_id, w.location) for w in self.session.query(Warehouse).all()]
        elif choice_table == 2:
            return [(i.inventory_id, i.user_id, i.result, i.warehouse_id) for i in self.session.query(Inventory).all()]
        elif choice_table == 3:
            return [(p.product_id, p.product_name, p.quantity) for p in self.session.query(Product).all()]
        elif choice_table == 4:
            return [(wp.inventory_id, wp.product_id) for wp in self.session.query(WarehouseProducts).all()]
        else:
            print("get_all_line error")

    def update_line_Warehouse(self, Warehouse_id, Where):
        warehouse = self.session.query(Warehouse).filter_by(warehouse_id=Warehouse_id).first()
        if warehouse:
            warehouse.location = Where
            self.session.commit()

    def update_line_Inventory(self, Inventory_id, User_id, Result, Warehouse_id):
        inventory = self.session.query(Inventory).filter_by(inventory_id=Inventory_id).first()
        warehouse = self.session.query(Warehouse).filter_by(warehouse_id=Warehouse_id).first()
        if not warehouse:
            print(f"Error: Warehouse_id {Warehouse_id} does not exist.")
            return 0
        if inventory:
            inventory.user_id = User_id
            inventory.result = Result
            inventory.warehouse_id = Warehouse_id
            self.session.commit()

    def update_line_Product(self, Product_id, Product_Name, Quantity):
        product = self.session.query(Product).filter_by(product_id=Product_id).first()
        if product:
            product.product_name = Product_Name
            product.quantity = Quantity
            self.session.commit()

    def update_line_Warehouse_Products(self, old_Inventory_id, old_Product_id, new_Inventory_id, new_Product_id):
        wp = self.session.query(WarehouseProducts).filter_by(inventory_id=old_Inventory_id, product_id=old_Product_id).first()
        if wp:
            wp.inventory_id = new_Inventory_id
            wp.product_id = new_Product_id
            self.session.commit()

    def delete_line(self, line_id, choice_table):
        if choice_table == 1:
            warehouse = self.session.query(Warehouse).filter_by(warehouse_id=line_id).first()
            if warehouse:
                self.session.delete(warehouse)
        elif choice_table == 2:
            inventory = self.session.query(Inventory).filter_by(inventory_id=line_id).first()
            if inventory:
                self.session.delete(inventory)
        elif choice_table == 3:
            product = self.session.query(Product).filter_by(product_id=line_id).first()
            if product:
                self.session.delete(product)
        self.session.commit()

    def delete_line_Warehouse_Products(self, Inventory_id, Product_id):
        wp = self.session.query(WarehouseProducts).filter_by(inventory_id=Inventory_id, product_id=Product_id).first()
        if wp:
            self.session.delete(wp)
            self.session.commit()

    def bulk_insert_warehouse(self, count):
        warehouses = [Warehouse(location=f"location{randint(1, 100)}") for _ in range(count)]
        self.session.bulk_save_objects(warehouses)
        self.session.commit()

    def bulk_insert_inventory(self, count):
        warehouse_ids = [w.warehouse_id for w in self.session.query(Warehouse).all()]
        if not warehouse_ids:
            print("Error: No warehouses exist. Please populate the Warehouse table first.")
            return

        inventories = []
        for _ in range(count):
            user_id = randint(1, 300)
            random_value = randint(1, 100) / 100
            if random_value < 0.45:
                result = "True"
            elif random_value < 0.90:
                result = "False"
            elif random_value < 0.92:
                result = "Unsuccessful"
            elif random_value < 0.95:
                result = "In process"
            else:
                result = "Planned"

            warehouse_id = warehouse_ids[randint(0, len(warehouse_ids) - 1)]
            inventories.append(Inventory(user_id=user_id, result=result, warehouse_id=warehouse_id))

        self.session.bulk_save_objects(inventories)
        self.session.commit()

    def bulk_insert_product(self, count):
        products = [
            Product(product_name=f"product{randint(1, 1000)}", quantity=randint(1, 1500))
            for _ in range(count)
        ]
        self.session.bulk_save_objects(products)
        self.session.commit()

    def bulk_insert_warehouse_products(self, count):
        inventory_ids = [i.inventory_id for i in self.session.query(Inventory).all()]
        product_ids = [p.product_id for p in self.session.query(Product).all()]

        if not inventory_ids or not product_ids:
            print("Error: Inventory or Product table is empty.")
            return

        combinations = [
            (inventory_id, product_id) for inventory_id in inventory_ids for product_id in product_ids
        ]
        if len(combinations) < count:
            print(f"Error: Not enough unique combinations. Maximum possible is {len(combinations)}.")
            return

        shuffle(combinations)
        warehouse_products = [
            WarehouseProducts(inventory_id=inv_id, product_id=prod_id)
            for inv_id, prod_id in combinations[:count]
        ]

        self.session.bulk_save_objects(warehouse_products)
        self.session.commit()

    def drop_all_tables(self):
        try:
            Base.metadata.drop_all(self.engine)
            print("All tables dropped successfully.")
        except Exception as e:
            print(f"Error while dropping tables: {e}")

    def search_all_entities(
            self,
            where_filter=None,
            inventory_id_filter=None,
            user_id_filter=None,
            result_filter=None,
            warehouse_id_filter=None,
            product_id_filter=None,
            product_name_filter=None,
            min_quantity=None,
            max_quantity=None,
    ):
        query = self.session.query(
            Warehouse.location.label("Where"),
            Warehouse.warehouse_id.label("Warehouse ID"),
            Inventory.inventory_id.label("Inventory ID"),
            Inventory.user_id.label("User ID"),
            Inventory.result.label("Result"),
            Product.product_id.label("Product ID"),
            Product.product_name.label("Product Name"),
            Product.quantity.label("Quantity"),
        ).join(Inventory, Warehouse.warehouse_id == Inventory.warehouse_id) \
            .join(WarehouseProducts, Inventory.inventory_id == WarehouseProducts.inventory_id) \
            .join(Product, WarehouseProducts.product_id == Product.product_id)

        if where_filter:
            query = query.filter(Warehouse.location.ilike(f"%{where_filter}%"))
        if inventory_id_filter:
            query = query.filter(Inventory.inventory_id == inventory_id_filter)
        if user_id_filter:
            query = query.filter(Inventory.user_id == user_id_filter)
        if result_filter:
            query = query.filter(Inventory.result.ilike(f"%{result_filter}%"))
        if warehouse_id_filter:
            query = query.filter(Warehouse.warehouse_id == warehouse_id_filter)
        if product_id_filter:
            query = query.filter(Product.product_id == product_id_filter)
        if product_name_filter:
            query = query.filter(Product.product_name.ilike(f"%{product_name_filter}%"))
        if min_quantity:
            query = query.filter(Product.quantity >= min_quantity)
        if max_quantity:
            query = query.filter(Product.quantity <= max_quantity)

        return query.all()

