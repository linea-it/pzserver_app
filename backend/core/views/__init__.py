from core.views.pipeline import PipelineViewSet
from core.views.process import ProcessViewSet
from core.views.product import ProductViewSet
from core.views.product_content import ProductContentViewSet
from core.views.product_file import ProductFileViewSet
from core.views.product_type import ProductTypeViewSet
from core.views.release import ReleaseViewSet
from core.views.user import (CsrfToOauth, GetToken, LoggedUserView, Logout,
                             UserViewSet)
