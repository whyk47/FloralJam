from django.core.paginator import Paginator, Page
from django.forms import Form, ModelForm
from django.http import HttpRequest
from django.urls import reverse
from typing import Optional, Iterable


class Invalid_Form(Exception):
    pass

def get_data(form: Form | ModelForm, exception: Exception=Invalid_Form, message: Optional[str]=None) -> dict:
    if form.is_valid():
        return form.cleaned_data
    else:
        if message:
            raise exception(message)
        raise exception(form.errors)

def get_page(request: HttpRequest, objects: Iterable) -> Page:
    paginator = Paginator(objects, 10)
    page_no = request.GET.get("page")
    page = paginator.get_page(page_no)
    return page

def url(host: str, page: str, args: Iterable) -> str:
    return host + reverse(f'floral_jamming:{page}', args=args)