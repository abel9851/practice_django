import logging
from functools import update_wrapper

from django.core.exceptions import ImproperlyConfigured
from django.template.response import TemplateResponse
from django.utils.functional import classproperty
from django.urls import reverse

from django.utils.decorators import classonlymethod
from django.http import (
    HttpResponseNotAllowed, HttpResponse,
    HttpResponseGone, HttpResponsePermanentRedirect, HttpResponseRedirect,
)

# django.request라는 로거 인스턴스를 가져오거나 생성
# logger는 logging systemd에서 메시지를 기록하는 객체다.
logger = logging.getLogger("django.request")

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
    # sanity checking은 프로그램의 기본 동작이나 데이터의 기본형태를 검사하는 간단한 검사를 의미한다.
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


# Reference https://docs.djangoproject.com/en/4.2/ref/class-based-views/base/#django.views.generic.base.View.http_method_not_allowed

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


class View:
    """
    Intentionally simple parent class for all views. Only implements
    dispatch-by-method and simple sanity checking.
    """

    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """

        for key, value in kwargs.items():
            setattr(self, key, value)
    # as_view = classonlymethod(as_view) 
    @classonlymethod # django.utils.decorators에서 확인해보면, python의 classmethod를 상속하고 있다. 별다른 수정없이 이름만 변경했다.
    def as_view(cls, **initkwargs): # request를 인자로 취하고 response를 리턴하는 view 함수를 리턴한다.
        """Main entry point for a request-response process."""

        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(
                    'The method name %s is not accepted as a keyword argument '
                    'to %s().' % (key, cls.__name__)
                )
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key)
                                ) # key는 repr()가 호출되어 TypeErrror에 출력된다.

        def view(request, *args, **kwargs):
            self = cls(**initkwargs) # view 클래스의 인스턴스를 생성한다. 위에서 정의한 init 메소드가 여기서 사용된다.
                                     # 클래스 메소드에서 사용하는 관례적인 self 인자가 아니라 as_view 메소드 안에서 지역변수로 사용됬다.
            self.setup(request, *args, **kwargs)
            if not hasattr(self, 'request'):
                raise AttributeError(
                    "%s instance has no 'request' attribute. Did you override "
                    "setup() and forget to call super()?" % cls.__name__
                )
            return self.dispatch(request, *args, **kwargs)

        view.view_class = cls # self를 사용하지 않고 cls를 사용하는 이유는, self는 인스턴스이고, cls는 클래스이기 때문이라고 생각한다.
                              # 즉, view 함수의 view_class attribute는 클래스를,
                              # self에는 인스턴스를 할당한다. 
                              # 그리고 self는 view.view_class를 정의할 시점에서는 아직 인스턴스가 생성되지 않은 상태(view가 호출되지 않았다.)이므로
                              # 사용할 수 없다. 
                              # 뷰 클래스의 인스턴스는 각 HTTP 요청마다 새로 생성되므로, view_class에 인스턴스를 할당하는 것은 적절하지 않다.
                              # self = cls(**initkwargs)가 그렇다.
        view.view_initkwargs = initkwargs

        # 반환해서 함수로 지정하는 것도 아닌데 어떻게 된거지?
        # 추측으로는 view안에 특별한 조치를 내부적으로 진행하는 것 같다.
        # take name and docstring from class
        # cls 즉 as_view를 호출한 view 클래스의 assigned 튜플에 정의된 __name__, __qualname__, __doc__, __annotations__를 view 메소드에 할당한다.
        update_wrapper(view, cls, updated=()) 

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        # cls.dispatch의 __dict__가 (updated 튜플의 default 요소) view 메소드에도 있다면, view 메소드의 __dict__에 cls.dispatch의 __dict__를 update한다.
        update_wrapper(view, cls.dispatch, assigned=())

        return view

    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        if hasattr(self, 'get') and not hasattr(self, 'head'): # self는 view 클래스의 인스턴스이다.
            self.head = self.get # head attr 즉, head method가 구현이 안되어 있을 경우에는 get을 할당한다. base view 자체에서도 구현이 안되어 있고, 보통 head 메서드는 많이들 구현하지 않는다.
        self.request = request # as_view()를 했을 떄 반환되는 view에 request를 할당한다.
        self.args = args # 마찬가지로 args와 kwargs를 할당한다.
        self.kwargs = kwargs

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    # request.path는 scheme, domain, quiry string을 포함하지 않은 request된 page의 path다.
    # https://docs.djangoproject.com/en/4.2/ref/class-based-views/base/#django.views.generic.base.View.http_method_not_allowed
    # http_method_not_allowed에서도 dispatch와 마찬가지로
    # 자기 역할만 하는 코드만 사용되어있고
    # http method 리스트는 별도의 메소드를 통해 가져오고 있다.
    def http_method_not_allowed(self, request, *args, **kwargs):
        # ex. WARNING: Method Not Allowed (POST): /example/path [Status Code: 405, Request Method: POST, Request Path: /example/path]
        logger.warning(
            'Method Not allowed (%s): %s', request.method, request.path,
            extra={'status_code': 405, 'request': request}
        )
        # HttpResponseNotAllowed는 HttpResponse를 상속하고 있다.
        return HttpResponseNotAllowed(self._allowed_methods())

    def option(self, request, *args, **kwargs):
        """Handle responding to requests for the OPTIONS HTTP verb."""
        response = HttpResponse()
        response.headers['Allow'] = ', '.join(self._allowed_methods())
        response.headers['Content-Length'] = '0'
        return response

    def _allowed_methods(self):
        # http_method_names 안에 지정된 메소드들 중에서도 view에 정의되어 있는 메소드들만을 return한다.
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]


# 231030에 classonlymethod, __get__, __get__에서 classmethod를 만드는 방법 공부.
# 231101에 공부할 것은 디스크립터 프로토콜의 __delete__, dispatch 이후, 복습은 setup 메소드가 하는 역할(3개)
# 231102에 복습해야할 것은 dispatch. obsidian에 내용 정리했으므로, 보면서 django doc도 보고 복습, 
# 디스크립터 프로토콜의 __delete__, deleter도 복습
# 다음으로 배워야할 것은 http_method_not_allowed.
# 231102 디스크립터 프로토콜 __get__, __set__, __delete__, getter, setter, deleter 복습 완료
# 습득한 것은 __set__을 포함한 매직 메소드들 안에서는 self._setter와 같은 setter로 지정한 메소드를 호출해야한다는 것.
# dispatch 복습하고 http_method_not_allowed, _allowed_methods, option 습득
# 231103 다음으로 할 것은 as_view의 update_wrapper 분석 하는것부터 시작.
# view의 base.py 분석이 끝나면 HttpRepsonse 분석 할 것.
# http_method_not_allowed, _allowed_methods, option 복습 완료
# update_wrapper, __name__, __qualname__, __doc__, __annotations__, __dict__, 
# update_wrapper의 updated, assigned 인자 습득완료
# 231104에 위의 2줄 복습하기
# update_wrapper 학습이 끝났으니 RedirectView 습득 시작하기
# 231106 RedirectView 습득완료, 하지만 django.urls의 reverse나 httpresponse는 아직 습득하지 않음
# templateview까지 습득 한뒤, reverse, httpresponse를 학습할 것
# 231107에 RedirectView의 get_redirect_url 메소드, get 메소드 복습할 것
# 231108 위의 두개 복습완료. templateView, ContextMixin, TemplateResponseMixin 습득완료
# 231108에 복습하기 완료.
# 231108 HttpResponse 습득 시작 django.http.response.py


# get 이외의 http 메소드로 접근할 시, 전부 get을 호출하는 것을 보면,
# 이 RedirectView는 무조건 유저에게 redirect url을 제공하고
# 그 url로 access 시키는 용도로 사용되는 것 같다.
# 개발자로서는 url의 변경으로 인해 다른 url에 로직을 작성하고
# 유저가 제대로 바뀐 곳으로 접속할 수 있도록 제어하는 용도로 사용하는 것 같다.
class RedirectView(View):
    """Provider a redirect on any GET request."""
    permanent = False
    url = None
    pattern_name = None
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        """
        Return the URL Redirect to. Keyword arguments from the URL pattern
        match generating the redirect request are provided as kwargs to this
        method.
        """
        if self.url:
            url = self.url % kwargs # example.com?pk=%%s
        elif self.pattern_name: # user-detail
            url = reverse(self.pattern_name, args=args, kwargs=kwargs)
        else:
            return None

        if args and self.query_string:
            url = "%s?%s" % (url, args)
        return url

    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        # 응답을 어떤 status code로 할지 정한다.
        # 검색엔진에 링크를 업데이트 시키냐 안시키냐.하는 부분까지도.
        if url:
            if self.permanent:
                return HttpResponsePermanentRedirect(url)
            else:
                return HttpResponseRedirect(url)
        else:
            logger.warning(
                'Gone: %s', request.path,
                extra={'status_code': 410, 'request': request}
            )
            return HttpResponseGone()

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, *kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


# get_context_data를 호출해서 얻은 데이터를 키워드 인자로 전달하는 기본 믹스인이다.
class ContextMixin:
    """
    a default context mixin that passes the keyward arguments received by
    get_context_data() as the template context.
    """

    extra_context = None

    # keyward arguments를 업데이트 및 self에 호출하는 클래스의 인스턴스 즉, view를 할당한다.
    # 딱히 코드 상에 view가 아니면 이 mixin을 사용할 수 없다는 제약같은건 없다.
    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self) # view라는 key로 self 인스턴스를 할당한다. 
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return kwargs    


class TemplateResponseMixin:
    """A mixin that can be used to render a template."""
    template_name = None
    template_engine = None
    response_class = TemplateResponse
    content_type = None

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        response_kwargs.setdefault('context')
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )

    def get_template_names(self):
        """
        Retirm a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response() is overridden.

        """
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateResonseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'"
            )

        else:
            return [self.template_name]


class TemplateView(TemplateResponseMixin, ContextMixin, View):
    """
    Render a template. Pass keyword arguments from the URLconf to the context.
    """

    # self.get_context_data는 ContextMixin에 정의되어 있다.
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs) # kwargs를 return 즉 context == kwargs
        return self.render_to_response(context) # view의 distpath 메소드에서 이 ger을 라우팅한 후, mixin에서 사용하는 httpresponse를 상속받아서 사용한다.
