from comics import ForbiddenPlanet
from schedule import every, repeat, run_pending
import time

#@repeat(every(1).minutes)
def main_stock_update():
    ForbiddenPlanet(get_live_sitemap=True)

"""
@repeat(every().day.at("21:00"))
def main_watchlist():
    push = ForbiddenPlanet(get_live_sitemap=False)
    push.run_watchlist_notification()
"""
@repeat(every().day.at("18:00"))
def main_stocklist():
    push = ForbiddenPlanet(get_live_sitemap=False)
    push.run_stocklist_notification()

"""
@repeat(every().day.at("21:05"))
def main_livelist():
    push = ForbiddenPlanet(get_live_sitemap=False)
    push.run_livelist_notification()
"""

if __name__ == '__main__':
    while True:
        run_pending()
        time.sleep(1)
    #main()
