import logging


class ContextMixin:
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data() as the template context.
    """

    extra_context = None

    def get_context_data(self, **kwargs):  # {'view': <__main__.ContextMixin object at 0x7f1159be9e20>}
        print("kwargs", kwargs)
        kwargs.setdefault("view", self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)  # {key: value} update
        return kwargs


class View:
    """
    Intentionally simple parent class for all views. Only implements
    dispatch-by-method and simple sanity checking.
    """

    # dispatch-by-method는 method에 따라요청을 분배하는 패턴
    # HTTP프로토콜에서 각 HTTP메소드들에 대해 다른 동작을 수행해야하는 경우, 이 패턴이 사용된다.
    # saninty checking은프로그램의 기본 동작이나 데이터의 기본형태를 검사하는 간단한 검사를 의미한다.
    # 예를 들어 입력 데이터가 특정 범위 내에 있는지, 특정형식을 갖추고 있는지 확인한다.

    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
        "trace",
    ]

    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguemnts, and othe things.
        """

        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        # kwargs를 살펴보고, 인스턴스에kwargs의 value를 저장하거나 에러를 발생시킨다.
        for key, value in kwargs.items():
            setattr(self, key, value)  # kwargs가 있다면, view 인스턴스에 key, value를 저장시킨다.
