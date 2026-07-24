def cart_count(request):
    if request.user.is_authenticated:
        return {"cart_count": sum(request.user.cart_items.values_list("quantity", flat=True))}
    return {"cart_count": 0}
