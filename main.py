from fpcomics import Notify

def main(mode='stocklist'):



    if mode = 'stock_update':
        Notify(get_live_sitemap = True)

    else:
        push = Notify(get_live_sitemap = False)
        if mode=='watchlist':
            push.run_watchlist_notification()
        
        elif mode=='stocklist':
            push.run_stocklist_notification()
        
        elif mode=='livelist':
            push.run_livelist_notification()
    
if __name__ == '__main__':
    main()
