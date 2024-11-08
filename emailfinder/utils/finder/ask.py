import requests
from random import randint, uniform
import time
from emailfinder.utils.agent import user_agent
from emailfinder.utils.file.email_parser import get_emails
from emailfinder.utils.color_print import print_info, print_ok

def search(target, total=50, proxies=None):
    ask_count = 10  # Ask tende a fornire un numero ridotto di risultati per pagina
    emails = set()
    url = f"https://www.ask.com/web?q=inbody:%40{target}&page="
    
    try:
        count = 1
        iter_count = int(total / ask_count)
        if (total % ask_count) != 0:
            iter_count += 1

        while count <= iter_count:
            new_url = url + str(count)
            headers = user_agent.get(randint(0, len(user_agent) - 1))
            response = requests.get(
                new_url,
                headers=headers,
                timeout=5,
                verify=False,
                proxies=proxies
            )
            text = response.text

            # Verifica se il contenuto HTML è valido prima di parsare
            if not text.strip().startswith("<!DOCTYPE html>") and not "<html" in text:
                print_info("Ask.com returned non-HTML content. Skipping parsing.")
                break

            # Estrai e aggiungi le email uniche al set
            emails.update(get_emails(target, text))

            # Pausa casuale tra le richieste per evitare il rilevamento
            time.sleep(uniform(2, 4))

            # Incrementa il contatore per passare alla pagina successiva
            count += 1

    except Exception as ex:
        print_info(f"Ask.com encountered an error: {ex}")

    emails = list(emails)
    if emails:
        print_ok(f"Ask.com discovered {len(emails)} unique emails")
    else:
        print_info("Ask.com did not discover any email IDs")
    return emails
