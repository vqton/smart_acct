from flask import Blueprint
from decimal import Decimal

views_bp = Blueprint('views', __name__, template_folder='../templates')

@views_bp.app_template_filter('vnd')
def _vnd_filter(value):
    if value is None:
        return '0'
    try:
        v = Decimal(str(value)).quantize(Decimal('0'))
        return '{:,.0f}'.format(v).replace(',', '.')
    except Exception:
        return str(value)

from . import auth_views, dashboard_views, coa_views, gl_views
from . import ar_views, ap_views, cash_views
from . import tax_views, fa_views, inventory_views
from . import payroll_views, budget_views, treasury_views
from . import fs_views, cc_views, costing_views, admin_views
