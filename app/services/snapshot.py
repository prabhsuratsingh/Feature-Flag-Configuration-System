from sqlalchemy.inspection import inspect


def model_to_dict(model) -> dict:
    return {
        attr.key: getattr(model, attr.key)
        for attr in inspect(model).mapper.column_attrs
    }
