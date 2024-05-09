class Invalid_Form(Exception):
    pass

def get_data(form, exception=Invalid_Form, message=None) -> dict:
    if form.is_valid():
        return form.cleaned_data
    else:
        if message:
            raise exception(message)
        raise exception(form.errors)
    
def multiply(x: int, y: int) -> int:
    return x * y