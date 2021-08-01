from .models import SubCategory, SubProduct


def category_context_processor(request):
    context = {}
    context['categorys'] = SubCategory.object.all()
    context['products'] = SubProduct.object.all()
    return context

# context_pro['product'] = SubProduct.object.all()
# , context_pro,context_pro = {}