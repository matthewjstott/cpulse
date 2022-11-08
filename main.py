from comics import ForbiddenPlanet
from schedule import every, repeat, run_pending

@repeat(every(1).minutes)
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
    main()
