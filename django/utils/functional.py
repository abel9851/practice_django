class classproperty:
    """
    Decorator that converts a method with a single cls argument into a property
    that can be accessed directly from the class.
    """

    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        # self는 classproperty 인스턴스 == 디스크립터 객체
        # instacne는 속성을 가져오려는 객체 == Test 인스턴스
        # cls는 속성을 가져오려는 객체의 클래스 == Test 클래스

        print("cls.__name__: ", cls.__name__)
        print("cls.__qualname__: ", cls.__qualname__)

        return self.fget(cls)  # 속성에 접근하면 cls를 인자로 주고 fget을 실행한다.

    def getter(self, method):  # getter는 @classproperty로 데코레이트된 메소드의 이름을 가진
        self.fget = method  # classproperty의 인스턴스의 fget에 메소드를 할당한다.
        return self  # 그 다음은 그 인스턴스를 반환한다.
