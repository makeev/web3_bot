from app import jinja
from sanic import response
from sanic.exceptions import NotFound
from project.models import User, Token, Contract, Transaction


models = [User, Token, Contract, Transaction]


def _get_model_by_name(name):
    for model in models:
        if model.collection.name == name:
            return model


@jinja.template("indexes.html")
async def indexes_view(request):
    indexes = {}
    for model in models:
        indexes[model.collection.name] = await model.collection.index_information()
    return {
        "models": models,
        "indexes": indexes,
    }


async def delete_index_view(request, model_name, index_name):
    model = _get_model_by_name(model_name)
    if not model:
        raise NotFound('Model not found')

    await model.collection.drop_index(index_name)
    return response.json({"success": True, "model_name": model.collection.name})


async def create_index_view(request, model_name):
    model = _get_model_by_name(model_name)
    if not model:
        raise NotFound('Model not found')

    field = request.form.get('field')
    await model.collection.create_index(field)

    return response.json({"success": True, "model_name": model.collection.name})


async def ensure_indexes_view(request, model_name):
    """
    Создать индексы модели по умолчанию,
    полезно после удаления и пересоздания таблицы
    """
    model = _get_model_by_name(model_name)
    if not model:
        raise NotFound('Model not found')

    await model.ensure_indexes()

    return response.json({"success": True})
