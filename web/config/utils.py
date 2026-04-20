from django.shortcuts import redirect
from functools import wraps

def login_or_guest_required(view_func):
    """
    로그인한 사용자이거나 세션에 'is_guest'가 True인 경우만 접근을 허용하는 데코레이터
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.get('is_guest'):
            return view_func(request, *args, **kwargs)
        return redirect('policy:login') # 로그인 페이지로 리다이렉트
    return _wrapped_view
