from django.urls import path, include
from . import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"menu-items", views.MenuItemView)

urlpatterns = [
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
    path("menu-items/category", views.CategoryView.as_view()),
    path("cart/menu-items", views.CartView.as_view()),
    path("orders", views.OrderItemView.as_view()),
    path("orders/<int:pk>", views.OrderDetailView.as_view()),
    path("groups/manager/users", views.ManagerGroupView.as_view()),
    path("groups/manager/users/<int:pk>", views.DeleteManagerRollView.as_view()),
    path("groups/delivery-crew/users", views.DeliveryGroupView.as_view()),
    path(
        "groups/delivery-crew/users/<int:pk>",
        views.DeleteDeliveryCrewRollView.as_view(),
    ),
]
