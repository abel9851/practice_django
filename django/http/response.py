
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

