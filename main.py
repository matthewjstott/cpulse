from comics import ForbiddenPlanet
from schedule import every, repeat, run_pending
import time



#@repeat(every(1).minutes)
def main_stock_update():
    ForbiddenPlanet(get_live_sitemap=True)


@repeat(every().day.at("21:05"))
def main_watchlist():
    push = ForbiddenPlanet(get_live_sitemap=False)
    push.run_watchlist_notification()


def main(mode='watchlist'):

    if mode == 'stock_update':
        ForbiddenPlanet(get_live_sitemap = True)

    else:
        push = ForbiddenPlanet(get_live_sitemap = False)
        if mode=='watchlist':
            push.run_watchlist_notification()
        
        elif mode=='stocklist':
            push.run_stocklist_notification()
        
        elif mode=='livelist':
            push.run_livelist_notification()
    
if __name__ == '__main__':
    while True:
        run_pending()
        time.sleep(1)
    #main()
