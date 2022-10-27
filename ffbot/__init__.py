from .constants import VERSION
from .optimizer import optimize  # noqa: F401,E402
from .scraper import current_week, scrape  # noqa: F401,E402
from .utils import load, save  # noqa: F401,E402

__version__ = VERSION
