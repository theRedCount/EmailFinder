import requests
from random import randint, uniform
import time
from emailfinder.utils.agent import user_agent
from emailfinder.utils.file.email_parser import get_emails
from emailfinder.utils.color_print import print_info, print_ok

def search(target, total=350, proxies=None):
    bing_count = 500
    emails = set()
    url = f"https://www.bing.com/search?q=inbody:'@{target}'&count={bing_count}"
    
    try:
        count = 0
        iter_count = int(total / bing_count)
        if (total % bing_count) != 0:
            iter_count += 1
            
        while count < iter_count:
            this_count = count * bing_count + 1
            new_url = url + f"&first={this_count}&FORM=PERE"
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
                print_info("Bing returned non-HTML content. Skipping parsing.")
                break
            
            # Estrai e aggiungi le email uniche al set
            emails.update(get_emails(target, text))

            # Aggiungi una pausa casuale per evitare il rilevamento come bot
            time.sleep(uniform(1, 3))

            # Incrementa il contatore per passare alla pagina successiva
            count += 1

    except Exception as ex:
        print_info(f"Bing encountered an error: {ex}")

    emails = list(emails)
    if emails:
        print_ok(f"Bing discovered {len(emails)} unique emails")
    else:
        print_info("Bing did not discover any email IDs")
    return emails
