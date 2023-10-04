from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class SerializerMixin:
    serialize_rules = ()

    def to_dict(self):
        data = {}
        for column in self.__table__.columns:
            data[column.name] = getattr(self, column.name)

        for rule in self.serialize_rules:
            if "." in rule:
                relationship, inner_attr = rule.split(".")
                rel_obj = getattr(self, relationship)
                if rel_obj:
                    if isinstance(rel_obj, list):
                        data[relationship] = [{inner_attr: getattr(item, inner_attr) for item in rel_obj}]
                    else:
                        data[relationship] = {inner_attr: getattr(rel_obj, inner_attr)}
            else:
                data[rule] = getattr(self, rule)

        return data

class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    reviews = db.relationship("Review", back_populates="customer")
    items = association_proxy('reviews', 'item')

    serialize_rules = ('id', 'name', 'reviews.comment')

class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    reviews = db.relationship("Review", back_populates="item")

    serialize_rules = ('id', 'name', 'price', 'reviews.comment')

class Review(db.Model, SerializerMixin):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    customer = db.relationship("Customer", back_populates="reviews")
    item = db.relationship("Item", back_populates="reviews")

    serialize_rules = ('id', 'comment', 'customer.id', 'item.id')
