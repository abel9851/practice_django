import logging

from django.core.exceptions import ImproperlyConfigured
from django.template.response import TemplateResponse
from django.utils.functional import classproperty


class ContextMixin:
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data() as the template context.
    """

    extra_context = None

    def get_context_data(self, **kwargs):
        kwargs.setdefault("view", self) # {'view': <__main__.ContextMixin object at 0x7f1159be9e20>}
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
    # sanity checking은프로그램의 기본 동작이나 데이터의 기본형태를 검사하는 간단한 검사를 의미한다.
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

    @classproperty
    def view_is_async(cls):
        # view가 비동기인지 아닌지 확인한다.
        # View를 상속받은 클래스 안에 있는 메소드나 클래스가 handlers 안에 들어간다.
        hanlders = [getattr(cls, method) for method in cls.http_method_names if (method != "options" and hasattr(cls, method))]
        # cls인 view 클래스에서,
        # http_method_names라는 리스트에는 get, post, put, patch, delete, head, options, trace가 있는데
        # 이 메소드들을 for loop한다.
        # 그때 if문으로 method가 options가 아니고, cls에
        # if not hanlders:
        #     return False
        # is_async = iscoroutinefunction(hanlders[0])
        # if not all(iscoroutinefunction(h) == is_async for h in handlers[1:]):
        #     raise ImpproperlyConfigured(f"{cls.__qualname__} HTTP hanlders must either be all sync or all " "async.")
        # return is_async

        print("handlers: ", hanlders)

    # @classonlymethod
    # def as_view(cls, **initkwargs):
    #     """Main entry point for a request-response process."""
    #     for key in initkwargs:
    #         if key in cls.http_method_names:
    #             raise TypeError("The method name %s is not acccepted as a keyword argument " "to %s()." % (key, cls.__name__))
    #         if not hasattr(cls, key):
    #             raise TypeError("%s() received an invalid keyword %r. as_view" "only accepts arguments that are already " "attributes of the class." % (cls.__name__, key))

    #     def view(request, *args, **kwargs):
    #         self = cls(**initkwargs)
    #         self.setput(request, *args, **kwargs)
    #         if not hasattr(self, "request"):
    #             raise AttributeError("%s instance has no 'request' attribute, Did you override" "setup() and forget to call super()?" % cls.__name__)
    #         return self.dispatch(request, *args, **kwargs)

    #     view.view_class = cls
    #     view.view_initkwargs = initkwargs

    #     # __name__ adn __qualname__ are intenitonally left unchanged as
    #     # view_class should be used to robustly determine the nae of the view
    #     # instead.
    #     view.__doc__ = cls.__doc__
    #     view.__moudule__ = cls.__module__
    #     view.__annotations__ = cls.dispatch.__annotations__
    #     # Copy possible attributes set by decorators, e.g. @csrf_exempt, form
    #     # the dispatch method.
    #     view.__dict__.update(cls.dispatch.__dict__)

    #     # Mark the callback if the view clas is async.
    #     if cls.view_is_async:
    #         markcoroutinefunction(view)

    #     return view  # 데코레이터의 원리와 같이, wrapper의 메소드를 호출하면 안에 정의한 메소드를 받게 된다.
    #     # 그 다음에 한번더 호출 하면 안에 정의한 view 함수가 호출된다.


class TestView(View):
    def get(self):
        pass

    def options(self):
        pass

    def post(self):
        pass

    class put:
        pass


# a = TestView()
# a.view_is_async


class TemplateResponseMixin:
    """A mixin that can be used to render a template."""

    template_name = None
    template_engine = None
    # response_class = TempleteResponse
    content_type = None

    def render_to_response(self, context, **response_kwargs):
        """ "
        Return a reponse, using the `response_class` for this view, with a
        templete renderd with th e given context.

        Pass response_kwargs to construtor of the response class.

        """
        # response class를 사용해서,받은 컨텍스트로 렌더링된 템플릿과 함께 리스폰스를 리턴한다.
        # content_type은, response_kwargs에 별도로 지정되어 전달된다.
        # ex) content_type: Application/X-FixedRecord

        response_kwargs.setdefault("content_type", self.content_type)
        print("response_kwargs: ", response_kwargs)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs,
        )

    def get_template_names(self):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requireds either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            # 설명에 쓰여있듯이, template_names라면, 변수 이름도 template_names로 하는게 맞는것 같은데
            # 왜 단수로 했는지 이해가 안간다.
            return [self.template_name]


class TemplateView(TemplateResponseMixin, ContextMixin, View):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs) # 키워드만 추가, get_context_data는 ContextMixin에 정의되어있다.
        return self.render_to_response(context) # render_to_response는 TemplateResponseMixin에 정의되어있다.
                                                # 이 떄 사용되는 response class는 template response이다.


class Redirectview(View):
    """Provide a redirect on any GET request."""
    permaent = False
    url = None
    pattern_name = None
    query_string = False
