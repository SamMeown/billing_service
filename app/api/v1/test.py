from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates/")
test = APIRouter()


@test.get("/form")
def form_post(request: Request):
    result = "Type a number"
    return templates.TemplateResponse('form.html', context={'request': request, 'result': result})


@test.post("/form")
def form_post(request: Request, num: int = Form(...)):
    result = num
    return templates.TemplateResponse('form.html', context={'request': request, 'result': result})
