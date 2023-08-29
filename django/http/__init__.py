# http 패키지(모듈) 안에 있는 모듈을 다른 모듈이나 패키지가 사용할 수 있도록
# 패키지(모듈) 이름 다음에 모듈 이름을 적어서 사용할 수 있도록 여기에 지정해놓기

from django.http.response import HttpResponse, HttpResponseBase

__all__ = ["HttpResponse", "HttpResponseBase"]
