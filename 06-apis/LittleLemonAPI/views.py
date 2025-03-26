from django.contrib.auth.models import User, Group
from django.utils.timezone import now

from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .models import Category, MenuItem, Cart, Order, OrderItem
from .permissions import IsSuperUser, IsManager, IsDeliveryCrew, IsCustomer
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    MenuItemUpdateSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
    AssignOrderSerializer,
    DeliveryStatusSerializer,
    AddCartSerializer,
    GetManagerSerializer,
    CreateManagerSerializer,
    GetDeliveryCrewSerializer,
    CreateDeliveryCrewSerializer,
    DeleteRollSerializer,
    OrderItemManagerSerializer,
)


class MenuItemView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    ordering_fields = ["price"]
    search_fields = ["category__title"]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return MenuItemUpdateSerializer
        return MenuItemSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "POST":
            permission_classes = [IsSuperUser | IsManager]
        elif self.request.method == "GET":
            permission_classes = [IsSuperUser | IsManager | IsCustomer | IsDeliveryCrew]
        elif (
            self.request.method == "PATCH"
            or self.request.method == "PUT"
            or self.request.method == "DELETE"
        ):
            permission_classes = [IsSuperUser | IsManager]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        if request.method == "DELETE":
            queryset = self.get_queryset()
            if not queryset.exists():
                return Response(
                    {"message": "No Menu item found"}, status=status.HTTP_404_NOT_FOUND
                )
        return super().list(request, *args, **kwargs)

    throttle_classes = [AnonRateThrottle, UserRateThrottle]


"""
class MenuItemView(
    generics.ListCreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView
):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ["price"]
    search_fields = ["category__title"]

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "POST":
            permission_classes = [IsSuperUser]
        elif self.request.method == "GET":
            permission_classes = [IsSuperUser | IsManager | IsCustomer | IsDeliveryCrew]
        elif self.request.method == "PATCH" or self.request.method == "PUT":
            permission_classes = [IsSuperUser | IsManager]
        return [permission() for permission in permission_classes]

    throttle_classes = [AnonRateThrottle, UserRateThrottle]


class MenuItemUpdeteView(
    generics.UpdateAPIView, generics.RetrieveAPIView, generics.DestroyAPIView
):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemUpdateSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "PATCH":
            permission_classes = [IsSuperUser | IsManager]
        elif self.request.method == "PUT":
            permission_classes = [IsSuperUser | IsManager]
        elif self.request.method == "GET":
            permission_classes = [IsSuperUser | IsManager | IsDeliveryCrew | IsCustomer]
        return [permission() for permission in permission_classes]

    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def list(self, request, *args, **kwargs):
        if request.method == "DELETE":
            queryset = self.get_queryset()
            if not queryset.exists():
                return Response(
                    {"message": "No Menu item found"}, status=status.HTTP_404_NOT_FOUND
                )
        return super().list(request, *args, **kwargs)

"""


class CategoryView(generics.ListCreateAPIView):
    def get_permissions(self):
        permission_classes = []
        if self.request.method == "POST":
            permission_classes = [IsSuperUser]
        elif self.request.method == "GET":
            permission_classes = [IsSuperUser | IsCustomer]

        return [permission() for permission in permission_classes]

    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)

    permission_classes = [IsCustomer]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartSerializer
        return CartSerializer

    def delete(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=self.request.user)
        if not cart.exists():
            return Response(
                {"message": "Cart is empyt"}, status=status.HTTP_404_NOT_FOUND
            )
        cart.delete()
        return Response({"message": "Cart items is deleted"}, status=status.HTTP_200_OK)


class OrderItemView(generics.ListCreateAPIView):
    def get_queryset(self):
        if (
            self.request.user.groups.filter(name="Manager").exists()
            or self.request.user.is_superuser
        ):
            return OrderItem.objects.all()
        elif self.request.user.groups.filter(name="Customer").exists():
            return OrderItem.objects.all().filter(order__user=self.request.user)
        elif self.request.user.groups.filter(name="Delivery crew").exists():
            return Order.objects.all().filter(delivery_crew=self.request.user)

    def get_serializer_class(self):
        if self.request.user.groups.filter(name="Delivery crew").exists():
            return OrderSerializer
        elif self.request.user.groups.filter(name="Manager").exists():
            return OrderItemManagerSerializer
        return OrderItemSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "GET":
            permission_classes = [IsSuperUser | IsManager | IsCustomer | IsDeliveryCrew]
        elif self.request.method == "POST":
            permission_classes = [IsCustomer]
        return [permission() for permission in permission_classes]

    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def post(self, request):
        carts = Cart.objects.filter(user=request.user)
        if not carts.exists():
            return Response(
                {"message": "Cart is empty"}, status=status.HTTP_404_NOT_FOUND
            )

        for cart in carts:
            order_data = {
                "user": cart.user.id,
                "status": False,
                "date": now().date(),
            }
            order_serializer = OrderSerializer(data=order_data)
            if order_serializer.is_valid():
                order = order_serializer.save()
            else:
                return Response(
                    order_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

            order_item_data = {
                "order": order.id,
                "menuitem": cart.menuitem.id,
                "quantity": cart.quantity,
                "unit_price": cart.unit_price,
                "price": cart.price,
            }

            order_item_serializer = OrderItemSerializer(data=order_item_data)
            if order_item_serializer.is_valid():
                order_item_serializer.save()
            else:
                return Response(
                    order_item_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

        carts.delete()

        return Response(
            {"message": "Order created successfully"},
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        if self.request.user.groups.filter(name="Delivery crew").exists():
            return Order.objects.all().filter(delivery_crew=self.request.user)
        elif self.request.user.groups.filter(name="Customer").exists():
            return OrderItem.objects.all().filter(order=self.request.user)
        elif self.request.user.groups.filter(name="Manager").exists():
            if self.request.method in ["PATCH", "PUT", "DELETE"]:
                return Order.objects.all()
        return OrderItem.objects.all()

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "GET":
            permission_classes = [IsManager | IsCustomer | IsDeliveryCrew]
        elif self.request.method in ["PUT", "DELETE"]:
            permission_classes = [IsManager]
        elif self.request.method == "PATCH":
            permission_classes = [IsManager | IsDeliveryCrew]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name="Delivery crew").exists():
                if self.request.method == "PATCH":
                    return DeliveryStatusSerializer
                else:
                    return OrderSerializer
            elif self.request.user.groups.filter(name="Manager").exists():
                if self.request.method == "PUT":
                    return AssignOrderSerializer
                elif self.request.method == "GET":
                    return OrderItemManagerSerializer
                elif self.request.method == "DELETE":
                    return OrderSerializer

        return OrderItemSerializer

    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        order.delete()
        return Response(
            {"message": "Order deleted successfully"}, status=status.HTTP_200_OK
        )


class ManagerGroupView(generics.ListCreateAPIView):
    permission_classes = [IsSuperUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        if self.request.method == "GET":
            managers = User.objects.all().filter(groups__name="Manager")
            return managers
        elif self.request.method == "POST":
            return User.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetManagerSerializer
        elif self.request.method == "POST":
            return CreateManagerSerializer


class DeleteManagerRollView(generics.DestroyAPIView):
    permission_classes = [IsSuperUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.all().filter(groups__name="Manager")
    serializer_class = DeleteRollSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": "No Manager found"}, status=status.HTTP_404_NOT_FOUND
            )
        return super().list(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        group = Group.objects.get(name="Manager")
        instance = self.get_object()
        instance.groups.remove(group)

        return Response(
            {"message": "Manager removed successfully"}, status=status.HTTP_200_OK
        )


class DeliveryGroupView(generics.ListCreateAPIView):
    permission_classes = [IsManager]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        if self.request.method == "GET":
            users = User.objects.all().filter(groups__name="Delivery crew")
            return users
        elif self.request.method == "POST":
            return User.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetDeliveryCrewSerializer
        elif self.request.method == "POST":
            return CreateDeliveryCrewSerializer


class DeleteDeliveryCrewRollView(generics.DestroyAPIView):
    permission_classes = [IsManager]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.all().filter(groups__name="Delivery crew")
    serializer_class = DeleteRollSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": "No Delivery crew found"}, status=status.HTTP_404_NOT_FOUND
            )
        return super().list(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        group = Group.objects.get(name="Delivery crew")
        instance = self.get_object()
        instance.groups.remove(group)

        return Response(
            {"message": "Delivery Crew removed successfully"}, status=status.HTTP_200_OK
        )


class TestView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
