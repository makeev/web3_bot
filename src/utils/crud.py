from math import ceil

from bson import ObjectId
from sanic.exceptions import NotFound


async def get_pagination_context_for(doc_class, request, limit, condition={}):
    """
    Return pagination context for defined model
    """
    page = int(request.args.get('page', 1))
    total = await doc_class.count_documents(condition)
    pages = range(1, ceil(total / limit) + 1)

    cursor = doc_class.find(condition).limit(limit).skip((page - 1) * limit).sort("$natural", -1)
    objects = await cursor.to_list(None)

    return {
        "objects": objects,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages
    }


async def get_object_or_404(cls, id):
    obj = await cls.find_one({"id": force_object_id(id)})
    if not obj:
        raise NotFound()

    return obj


async def get_list(cls, filter_=None, sort=None, limit=None):
    cursor = cls.find(filter_)

    if sort:
        cursor = cursor.sort(sort)

    if limit:
        cursor = cursor.limit(limit)

    return await cursor.to_list(length=None)


async def create_object(cls, **kwargs):
    obj = cls(**kwargs)
    r = await obj.commit()
    return obj, r


async def update_by_id(cls, id, **kwargs):
    obj = await get_object_or_404(cls, force_object_id(id))
    for key, value in kwargs.items():
        setattr(obj, key, value)

    r = await obj.commit()
    return obj, r


async def delete_by_id(cls, id):
    obj = await get_object_or_404(cls, force_object_id(id))
    return await obj.delete()


def force_object_id(id):
    if type(id) != ObjectId:
        return ObjectId(id)
    return id
