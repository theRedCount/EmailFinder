import requests
from random import randint, uniform
import time
from emailfinder.utils.agent import user_agent
from emailfinder.utils.file.email_parser import get_emails
from emailfinder.utils.color_print import print_info, print_ok

def search(target, total=50, proxies=None):
    reddit_count = 10
    emails = set()
    url = f"https://www.reddit.com/search.json?q=%40{target}&sort=new&limit={reddit_count}"
    headers = user_agent.get(randint(0, len(user_agent) - 1))
    headers.update({"User-Agent": "Mozilla/5.0 (compatible; EmailFinderBot/1.0)"})  # Reddit richiede uno User-Agent specifico
    
    try:
        after = None
        count = 0
        iter_count = int(total / reddit_count)
        if (total % reddit_count) != 0:
            iter_count += 1

        while count < iter_count:
            # Aggiungi il parametro `after` per paginare attraverso i risultati
            new_url = url + (f"&after={after}" if after else "")
            response = requests.get(
                new_url,
                headers=headers,
                timeout=5,
                proxies=proxies
            )

            # Controllo dell'errore di accesso
            if response.status_code == 429:  # Too many requests
                print_info("Reddit API rate limit exceeded. Pausing and retrying...")
                time.sleep(10)  # Pausa di 10 secondi per evitare il blocco
                continue
            elif response.status_code != 200:
                print_info(f"Reddit API returned an error: {response.status_code}")
                break

            data = response.json()
            if 'data' in data and 'children' in data['data']:
                posts = data['data']['children']
                for post in posts:
                    text = post['data'].get('selftext', '') + " " + post['data'].get('title', '')
                    # Estrai e aggiungi le email uniche al set
                    emails.update(get_emails(target, text))

                # Se ci sono altri risultati, aggiorna `after` per paginare, altrimenti esci
                after = data['data'].get('after')
                if not after:
                    break

            # Attesa casuale tra le richieste per evitare il rilevamento
            time.sleep(uniform(2, 5))
            count += 1

    except Exception as ex:
        print_info(f"Reddit encountered an error: {ex}")

    emails = list(emails)
    if emails:
        print_ok(f"Reddit discovered {len(emails)} unique emails")
    else:
        print_info("Reddit did not discover any email IDs")
    return emails
