import requests
from random import randint, uniform
import time
from emailfinder.utils.agent import user_agent
from emailfinder.utils.file.email_parser import get_emails
from emailfinder.utils.color_print import print_info, print_ok

def search(target, total=350, proxies=None):
    duck_count = 50
    emails = set()
    url = f"https://html.duckduckgo.com/html?q=inbody:'@{target}'&count={duck_count}"
    
    try:
        count = 0
        iter_count = int(total / duck_count)
        if (total % duck_count) != 0:
            iter_count += 1
            
        while count < iter_count:
            new_url = url + f"&s={count * duck_count}"
            headers = user_agent.get(randint(0, len(user_agent) - 1))
            response = requests.get(
                new_url,
                headers=headers,
                timeout=5,
                verify=False,
                proxies=proxies
            )
            text = response.text

            # Verifica se la risposta contiene HTML valido prima di parsare
            if not text.strip().startswith("<!DOCTYPE html>") and not "<html" in text:
                print_info("DuckDuckGo returned non-HTML content. Skipping parsing.")
                break
            
            # Estrai e aggiungi le email uniche al set
            emails.update(get_emails(target, text))

            # Aggiungi una pausa casuale per evitare il rilevamento come bot
            time.sleep(uniform(1, 3))

            # Incrementa il contatore per passare alla pagina successiva
            count += 1

    except Exception as ex:
        print_info(f"DuckDuckGo encountered an error: {ex}")

    emails = list(emails)
    if emails:
        print_ok(f"DuckDuckGo discovered {len(emails)} unique emails")
    else:
        print_info("DuckDuckGo did not discover any email IDs")
    return emails
