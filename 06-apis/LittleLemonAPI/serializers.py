from datetime import date

from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Category, MenuItem, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category"]


class MenuItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["featured"]


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["id", "user", "menuitem", "quantity", "unit_price", "price"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "status", "date"]


class AssignOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["delivery_crew"]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "order", "menuitem", "quantity", "unit_price", "price"]


class OrderItemManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "order", "menuitem", "quantity", "unit_price", "price"]
        depth = 1


class DeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]


class AddCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    unit_price = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True
    )
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["user", "menuitem", "quantity", "unit_price", "price"]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        menu_item = get_object_or_404(MenuItem, title=validated_data["menuitem"])
        validated_data["unit_price"] = menu_item.price
        validated_data["price"] = menu_item.price * validated_data["quantity"]

        return super().create(validated_data)


class AddOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    date = serializers.DateField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "date"]

    def create(self, validated_data):
        dataset = get_object_or_404(Cart, pk=validated_data["id"])
        validated_data["user"] = dataset.user
        validated_data["date"] = date.today()

        return super().create(validated_data)


class AddOrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    menuitem = serializers.CharField(max_length=255, read_only=True)
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True
    )
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["order", "menuitem", "quantity", "unit_price", "price"]

    def create(self, validated_data):
        dataset = Cart.objects.get(pk=validated_data["id"])
        validated_data["order"] = dataset.user
        validated_data["menuitem"] = dataset.menuitem
        validated_data["quantity"] = dataset.quantity
        validated_data["unit_price"] = dataset.unit_price
        validated_data["price"] = dataset.price

        return super().create(validated_data)


class GetManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class CreateManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password", "groups"]

    def create(self, validated_data):
        validated_data["groups"] = [1]
        return super().create(validated_data)


class DeleteRollSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["groups"]

    def update(self, instance, validation_data):
        instance.groups.clear()
        instance.save()

        return instance


class GetDeliveryCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class CreateDeliveryCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password", "groups"]

    def create(self, validated_data):
        validated_data["groups"] = [2]
        return super().create(validated_data)
