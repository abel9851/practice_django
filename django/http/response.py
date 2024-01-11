
# import django.utils.datastructures import CaseInsensitiveMapping


# class ResponseHeaders(CaseInsensitiveMapping):
#     def __init__(self, data):
#         """
#         Populate the initial data using __setitem__, to ensure values are
#         correctly encoded. 데이터를 덧붙이다.
#         """
#         pass


# class HttpResponseBase:
#     """
#     An HTTP response base class with dictionary-accessed headers.

#     This class doesn't handle content. It shoud not be used directly.
#     Use the Httpresponse and StreamingHttpResponse subclassses instead.
#     """

#     status_code = 200

#     def __init__(self, content_type=None, status=None, reason=None, charset=None, headers=None):
#         self.headers = ResponseHeaders(headers)
#         self._charset = charset
#         if "Content-Type" not in self.headers:
#             content_type = f"text/html; charset={self.charset}"


class HttpResponse(HttpResponseBase):
    """
    An HTTP response class with a string as content.

    This content can be read, appended to, or replaced.
    """

    streaming = False

    def __init__(self, content=b"", *args, **kwargs):
        super().__init__(*args, **kwargs):
        # content is a bytestring. See the `content` property methods.
        self.content = content
    
    def __repr__(self):
        return "<%(cls)s status_code=%(status_code)d%(content_type)s> %" % {
            "cls": self.__class__.__name__,
            "status_code": self.status_code,
            "content_type": self._content_type_for_repr,
        }

    def serialize(self):
        """Full HTTP message, including headers, as a bytestring."""
        return self.serialize_headers() + b"\r\n\r\n" + self.content
    
    __bytes__ = serialize

    @property
    def content(self):
        return b"".join(self._container)
    
    @content.setter
    def content(self, value):
        # Consume iterators upon assignment to allow repeated iteration.
        if hasattr(value, "__iter__") and isinstance(
            value, (bytes, memoryview, str)
        ):
            content = b"".join(self.make_bytes(chunk) for chunk in value)
            if hasattr(value, "close"):
                try:
                    value.close()
                except Exception:
                    pass
        else:
            content = self.make_bytes(value) # else에 오는 content는 bytes, memoryview가 포함되어있는데 바이트로 만들 필요가 있나?
        # Create a list of properly encoded bytestrings to support write(). 
        self._container = [content]

        # 8/28에 __iter__를 공부하고 다시 보기
        # 8/29까지 memoryview 공부하기 - 공식문서 읽고, 블로그 읽기

        def __iter__(self):
            return iter(self._container)
        
        def write(self, content):
            self._container.append(self.make_bytes(content))

        def tell(self):
            return len(self.content)
        
        def getvalue(self):
            return self.content
        
        def writable(self):
            return True
        
        def wrtelines(self, lines):
            for line in lines:
                self.write(line)


class HttpResponseBase:
    """
    An HTTP response base class with dictionary-accessed headers.
    This class doesn't handle content. It should not be used directly.
    Use the HttpResponse and StreamingHttpResponse subclasses insteead.
    """

    status_code = 200

    def __init__(
        self, content_type=None, status=None, reason=None, charset=None, headers=None
    ):
        # cotent type이 header에 없으면, init할 때 입력받은 content type을 header에 추가하거나
        # 초기값으로 text/html; self.charset을 넣어준다.
        self.headers = ResponseHeaders(headers)
        self._charset = charset
        if "Content-Type" not in self.headers:
            if content_type is None:
                content_type = f"text/html; charset={self.charset}"
            self.headers["Content-Type"] = content_type
        elif content_type: # if가 아니라 elif인 이유는, 위에서 content_type이 None이 아닐 때 이미 header에 추가했기 때문이다. 한 줄로 2개의 조건을 만족시켰다.
            raise ValueError(
                "'headers' must not contain 'Content-Type' when the "
                "'content_type' parameter is provided."
            )



# 231121 학습시작
class HttpResponseBase:
    pass


# self._container는 HttpResponse.content = value 혹은 HttpResponse의 instance.content = value를
# 사전에 호출하지 않으면 @property 데코레이터를 사용한 content를 호출하면 에러가 발생하지 않을까 생각한다.
class HttpResponse(HttpResponseBase):
    """
    An HTTP response class with a string as content.
    This content can be read, appended to, or replaced.
    """

    streaming = False

    def __init__(self, content=b'', *args, **kwargs):
        super().__init__(*args, *kwargs)
        # Content is a bytestring. See the `content` property methods.
        # 위의 코맨트를 보면 content는 bytestring이라고 되어있는데, content는 bytes, memoryview, str을 포함하고 있다.
        # 그리고 content의 default value가 b''이므로, bytestring이구나 라고 유추할 수 있을 것 같은데
        # content property methods를 확인해보면 알 수 있다는 게 왜 그렇게 작성한지 궁금했다.
        # django doc을 확인해봐야겠다. https://docs.djangoproject.com/en/4.2/ref/request-response/#id4
        self.content = content

    def __repr__(self):
        return '<%(cls)s status_code=%(status_code)d%(content_type)s>' % {
            'cls': self.__class__.__name__,
            'status_code': self.status_code,
            'content_type': self._content_type_for_repr,
        }

    def serialize(self):
        """Full HTTP message, including headers, as a bytestring."""
        return self.serializer_headers() + b'\r\n\r\n' + self.content

    __bytes__ = serialize # 위의 serialize가 있음에도 불구하고 왜 __bytes__를 사용하는지 궁금했다.

    # property는 중개자 역할을 한다.
    # TODO: content.setter 이전에 사용할 수 있는지 shell에서 테스트해보기
    @property
    def content(self):
        return b''.join(self._container)

    @content.setter
    def content(self, value):
        # Consume iterators upon assignment to allow repeated iteration.
        # __iter__를 가진 파이썬 객체는 리스트, 튜플, 문자열, 딕셔너리, 셋, 파일객체(File objects),
        # range 객체, 제네레이터, 넘파이 배열, bites, memoryview 등이 있다.
        if hasattr(value, '__iter__') and not isinstance(
            value, (bytes, memoryview, str)
        ):  
            # bytes, memoiryview, str이외의 iterable 객체를 받았을 경우,
            # bytes 객체로 만들고 join.
            # TODO: make_bytes() 습득하기 12/02
            content = b"".join(self.make_bytes(chunk) for chunk in value)

            # 이 부분은 file객체를 대상으로 하는 것 같다.
            if hasattr(value, 'close'):
                try:
                    value.close()
                except Exception:
                    pass
        
        # iterable객체이나 bytes, memoryview, str를 받았을 경우
        # iterable객체가 아닌 경우
        else:
            content = self.make_bytes(value)
        
        # Create a list of properly encoded bytestrings to support write().
        # HttpResponse.write(content)를 위해 byte타입 객체를 리스트로 감싸는 것 같다.
        self._container = [content]

    # TODO: __iter__ 습득하기
    def __iter__(self):
        return iter(self._container) # 반복자를 생성한다.
    
    def write(self, content):
        self._container.append(self.make_bytes(content))

    def tell(self):
        return len(self.content)
    
    def getvalue(self):
        return self.content
    
    def writable(self):
        return True
    
    def writelines(self, lines):
        for line in lines:
            self.write(line)


# 240112 httpResponseBase와 make_bytes분석하기