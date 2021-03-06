import random
import string

from slugify import slugify


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def unique_order_id_generator(instance):
    """
    This is for a Django project and it assumes your instance
    has a model with a order_id field and a title character (char) field.
    """
    order_id = random_string_generator(chars=string.ascii_uppercase + string.digits)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(order_id=order_id).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return order_id


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name)

    Klass = instance.__class__
    qs_exists = Klass.query.filter_by(slug=slug).scalar()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug, randstr=random_string_generator(size=4)
        )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug
